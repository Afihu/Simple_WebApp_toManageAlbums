"""ImageService - DynamoDB + S3 backed implementation with presigned URL support.

Environment Variables expected:
    DYNAMODB_TABLE - table name storing all entities (single-table design)
    IMAGES_BUCKET  - S3 bucket name for image binary objects

Data storage patterns:
    DynamoDB PK/SK: (user_id, type='image#<image_id>')
    S3 Object Key:  '{user_id}/{album_id}/{image_id}' always prefixed by user_id

Image Upload Flow:
    1. generate_upload_url() - Creates pending image record + presigned PUT URL
    2. Client uploads directly to S3 using presigned URL
    3. confirm_upload() - Marks image as active after successful upload
    
Image Download Flow:
    1. generate_download_url() - Returns presigned GET URL for active images
    2. Client downloads directly from S3 using presigned URL
"""
from __future__ import annotations
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from ..models.image import Image
from .validation import validate_name, normalize_description, ValidationError


TABLE_NAME = os.getenv("DYNAMODB_TABLE", "AlbumsApp")
IMAGES_BUCKET = os.getenv("IMAGES_BUCKET", "my-albums-and-images-bucket")


class ImageService:
    def __init__(self, dynamodb_resource=None, s3_client=None):
        """Initialize service with default boto3 resolution.

        IMAGES_BUCKET taken from env var IMAGES_BUCKET."""
        self.dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self.s3 = s3_client or boto3.client("s3")
        self.table = self.dynamodb.Table(TABLE_NAME)

    @staticmethod
    def _image_sort_key(image_id: str) -> str:
        return f"image#{image_id}"

    def list_images(self, user_id: str, album_id: str, include_pending: bool = False) -> List[Dict]:
        resp = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id) &
            boto3.dynamodb.conditions.Key("type").begins_with("image#")
        )
        items = [i for i in resp.get("Items", []) if i.get("album_id") == album_id]
        
        # Filter by status if not including pending
        if not include_pending:
            items = [i for i in items if i.get("status") == "active"]
            
        return [self._item_to_image_dict(i) for i in items]

    def generate_upload_url(self, user_id: str, album_id: str, name: str, description: Optional[str], size_bytes: int, content_type: str) -> Dict:
        """Generate presigned upload URL and create pending image record."""
        name = validate_name(name)
        description = normalize_description(description)
        image_id = str(uuid.uuid4())
        s3_key = f"{user_id}/{album_id}/{image_id}"
        
        # Create pending image record
        image = Image(
            image_id=image_id, 
            album_id=album_id, 
            user_id=user_id, 
            name=name, 
            description=description, 
            size_bytes=size_bytes, 
            content_type=content_type, 
            s3_key=s3_key,
            status="pending"
        )
        item = {
            "user_id": user_id,
            "type": self._image_sort_key(image_id),
            **image.to_dict(),
        }
        self.table.put_item(Item=item)
        
        # Generate presigned URL for upload (expires in 15 minutes)
        try:
            upload_url = self.s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': IMAGES_BUCKET,
                    'Key': s3_key,
                    'ContentType': content_type
                },
                ExpiresIn=900  # 15 minutes
            )
        except ClientError:
            # Rollback DynamoDB item if presigned URL generation fails
            self.table.delete_item(Key={"user_id": user_id, "type": self._image_sort_key(image_id)})
            raise
            
        return {
            "upload_url": upload_url,
            "image_id": image_id,
            "expires_in": 900
        }

    def confirm_upload(self, user_id: str, album_id: str, image_id: str) -> Optional[Dict]:
        """Confirm successful upload and mark image as active."""
        try:
            # Check if image record exists and is pending
            image = self.get_image(user_id, album_id, image_id)
            if not image or image.get("status") != "pending":
                return None
            
            # Verify S3 object exists and has content
            try:
                response = self.s3.head_object(Bucket=IMAGES_BUCKET, Key=image["s3_key"])
                actual_size = response.get('ContentLength', 0)
                if actual_size == 0:
                    return None  # Upload not completed or failed
            except ClientError:
                return None  # S3 object doesn't exist
            
            # Update image status to active and actual size
            update_expr = "SET #status = :status, #updated_at = :updated_at, #size_bytes = :size"
            expr_vals = {
                ":status": "active",
                ":updated_at": datetime.utcnow().isoformat(),
                ":size": actual_size
            }
            expr_names = {
                "#status": "status",
                "#updated_at": "updated_at", 
                "#size_bytes": "size_bytes"
            }
            
            resp = self.table.update_item(
                Key={"user_id": user_id, "type": self._image_sort_key(image_id)},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_vals,
                ExpressionAttributeNames=expr_names,
                ReturnValues="ALL_NEW",
            )
            return self._item_to_image_dict(resp.get("Attributes", {}))
        except ClientError:
            return None

    def generate_download_url(self, user_id: str, album_id: str, image_id: str) -> Optional[Dict]:
        """Generate presigned download URL for active images."""
        image = self.get_image(user_id, album_id, image_id)
        if not image or image.get("status") != "active":
            return None
            
        try:
            download_url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': IMAGES_BUCKET,
                    'Key': image["s3_key"]
                },
                ExpiresIn=900  # 15 minutes
            )
            return {
                "download_url": download_url,
                "expires_in": 900,
                "content_type": image.get("content_type"),
                "size_bytes": image.get("size_bytes")
            }
        except ClientError:
            return None

    def create_image(self, user_id: str, album_id: str, name: str, description: Optional[str], size: int, content_type: Optional[str] = None) -> Dict:
        """Legacy method - use generate_upload_url() + confirm_upload() instead."""
        name = validate_name(name)
        description = normalize_description(description)
        image_id = str(uuid.uuid4())
        s3_key = f"{user_id}/{album_id}/{image_id}"  # validated path; user_id prefix
        image = Image(image_id=image_id, album_id=album_id, user_id=user_id, name=name, description=description, size_bytes=size, content_type=content_type, s3_key=s3_key, status="active")
        item = {
            "user_id": user_id,
            "type": self._image_sort_key(image_id),
            **image.to_dict(),
        }
        self.table.put_item(Item=item)
        # Placeholder empty object (allows future overwrite with actual content)
        try:
            self.s3.put_object(
                Bucket=IMAGES_BUCKET,
                Key=s3_key,
                Body=b"",  # zero-length placeholder
                Metadata={"album_id": album_id, "image_id": image_id},
                ContentType=content_type or "application/octet-stream",
            )
        except ClientError:
            # Rollback DynamoDB item if S3 fails to keep consistency (best-effort)
            self.table.delete_item(Key={"user_id": user_id, "type": self._image_sort_key(image_id)})
            raise
        return image.to_dict()

    def get_image(self, user_id: str, album_id: str, image_id: str) -> Optional[Dict]:
        resp = self.table.get_item(Key={"user_id": user_id, "type": self._image_sort_key(image_id)})
        item = resp.get("Item")
        if not item or item.get("album_id") != album_id:
            return None
        return self._item_to_image_dict(item)
    
    def get_album_id_for_image(self, user_id: str, image_id: str) -> Optional[str]:
        """Get the album_id for a given image_id owned by user_id."""
        resp = self.table.get_item(Key={"user_id": user_id, "type": self._image_sort_key(image_id)})
        item = resp.get("Item")
        if not item:
            return None
        return item.get("album_id")

    def update_image(self, user_id: str, album_id: str, image_id: str, name: Optional[str], description: Optional[str]) -> Optional[Dict]:
        update_expr = []
        expr_vals: Dict[str, Any] = {":u": datetime.utcnow().isoformat()}
        expr_names: Dict[str, str] = {"#updated_at": "updated_at"}
        if name:
            name = validate_name(name)
            update_expr.append("#name = :n")
            expr_vals[":n"] = name
            expr_names["#name"] = "name"
        if description is not None:
            description = normalize_description(description)
            update_expr.append("#description = :d")
            expr_vals[":d"] = description
            expr_names["#description"] = "description"
        update_expr.append("#updated_at = :u")
        if not update_expr:
            return self.get_image(user_id, album_id, image_id)
        try:
            resp = self.table.update_item(
                Key={"user_id": user_id, "type": self._image_sort_key(image_id)},
                UpdateExpression="SET " + ", ".join(update_expr),
                ExpressionAttributeValues=expr_vals,
                ExpressionAttributeNames=expr_names,
                ReturnValues="ALL_NEW",
            )
        except ClientError:
            return None
        attrs = resp.get("Attributes", {})
        if attrs.get("album_id") != album_id:
            return None
        return self._item_to_image_dict(attrs)

    def delete_image(self, user_id: str, album_id: str, image_id: str) -> bool:
        try:
            existing = self.get_image(user_id, album_id, image_id)
            if not existing:
                return False
            self.table.delete_item(Key={"user_id": user_id, "type": self._image_sort_key(image_id)})
            # Delete S3 object (ignore if missing)
            try:
                self.s3.delete_object(Bucket=IMAGES_BUCKET, Key=existing['s3_key'])
            except ClientError:
                pass
            return True
        except ClientError:
            return False

    @staticmethod
    def _item_to_image_dict(item: Dict[str, Any]) -> Dict:
        keys = [
            "image_id",
            "album_id",
            "user_id",
            "name",
            "description",
            "s3_key",
            "size_bytes",
            "content_type",
            "status",
            "created_at",
            "updated_at",
        ]
        return {k: item.get(k) for k in keys}

