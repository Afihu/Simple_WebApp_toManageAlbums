"""AlbumService - DynamoDB backed implementation (placeholders for credentials).

Environment Variables expected:
  DYNAMODB_TABLE - table name (AlbumsApp)

The table uses (user_id, type) as PK/SK. Albums stored with type 'album#<album_id>'.
"""
from __future__ import annotations
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from ..models.album import Album
from .validation import validate_name, normalize_description, ValidationError


TABLE_NAME = os.getenv("DYNAMODB_TABLE", "AlbumsApp")


class AlbumService:
    def __init__(self, dynamodb_resource=None):
        """Initialize service.

        Uses default boto3 credential/region resolution. Table name taken from
        env var DYNAMODB_TABLE (see data-model spec)."""
        self.dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(TABLE_NAME)

    # --- Internal helpers ---
    @staticmethod
    def _album_sort_key(album_id: str) -> str:
        return f"album#{album_id}"

    # DynamoDB single-table design:
    #   PK: user_id
    #   SK: type = "album#<album_id>"
    # This allows fast per-user album listing with begins_with('album#').

    def list_albums(self, user_id: str) -> List[Dict]:
        resp = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id) &
            boto3.dynamodb.conditions.Key("type").begins_with("album#")
        )
        items = resp.get("Items", [])
        return [self._item_to_album_dict(i) for i in items]

    def create_album(self, user_id: str, name: str, description: Optional[str]) -> Dict:
        name = validate_name(name)
        description = normalize_description(description)
        album_id = str(uuid.uuid4())
        album = Album(album_id=album_id, user_id=user_id, name=name, description=description)
        item = {
            "user_id": user_id,
            "type": self._album_sort_key(album_id),
            **album.to_dict(),
        }
        self.table.put_item(Item=item)
        return album.to_dict()

    def get_album(self, user_id: str, album_id: str) -> Optional[Dict]:
        resp = self.table.get_item(Key={"user_id": user_id, "type": self._album_sort_key(album_id)})
        item = resp.get("Item")
        if not item:
            return None
        return self._item_to_album_dict(item)

    def update_album(self, user_id: str, album_id: str, name: Optional[str], description: Optional[str]) -> Optional[Dict]:
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
            return self.get_album(user_id, album_id)
        try:
            resp = self.table.update_item(
                Key={"user_id": user_id, "type": self._album_sort_key(album_id)},
                UpdateExpression="SET " + ", ".join(update_expr),
                ExpressionAttributeValues=expr_vals,
                ExpressionAttributeNames=expr_names,
                ReturnValues="ALL_NEW",
            )
        except ClientError:
            return None
        return self._item_to_album_dict(resp.get("Attributes", {}))

    def delete_album(self, user_id: str, album_id: str) -> bool:
        try:
            self.table.delete_item(Key={"user_id": user_id, "type": self._album_sort_key(album_id)})
            return True
        except ClientError:
            return False

    @staticmethod
    def _item_to_album_dict(item: Dict[str, Any]) -> Dict:
        # Convert a raw DynamoDB item to public dict (already mostly aligned)
        keys = [
            "album_id",
            "user_id",
            "name",
            "description",
            "image_count",
            "created_at",
            "updated_at",
        ]
        return {k: item.get(k) for k in keys}

