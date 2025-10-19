"""Lambda handlers for /albums/{album_id}/images endpoints with presigned URL support."""
import json
from typing import Any

from ..services.image_service import ImageService
from ..services.quota_service import QuotaService
from ..services.validation import ValidationError
from . import utils

image_service = ImageService()
quota_service = QuotaService()


def create_image_legacy(event, context):  # Legacy POST /albums/{album_id}/images (deprecated)
    """Legacy endpoint - use generate_upload_url + confirm_upload instead."""
    user_id = utils.get_user_id(event)
    album_id = event.get("pathParameters", {}).get("album_id")
    if not album_id:
        return utils.bad_request("album_id missing")
        
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return utils.bad_request("Invalid JSON body")
        
    name = (payload.get("name") or "").strip()
    if not name:
        return utils.bad_request("'name' is required")
        
    size = int(payload.get("size_bytes") or payload.get("size") or 0)
    if size <= 0:
        size = 1024  # default 1KB placeholder
        
    if not quota_service.can_add(user_id, size):
        return utils.bad_request("Quota exceeded")
        
    description = payload.get("description")
    try:
        image = image_service.create_image(user_id, album_id, name=name, description=description, size=size)
    except ValidationError as e:
        return utils.bad_request(str(e))
        
    quota_service.add_usage(user_id, size)
    return utils.created(image)





def generate_upload_url(event, context):  # POST /albums/{album_id}/images/upload-url
    user_id = utils.get_user_id(event)
    album_id = event.get("pathParameters", {}).get("album_id")
    if not album_id:
        return utils.bad_request("album_id missing")
    
    # Import here to avoid circular import
    from ..services.album_service import AlbumService
    album_service = AlbumService()
    
    # Validate album ownership
    album = album_service.get_album(user_id, album_id)
    if not album:
        return utils.unauthorized("User does not own the album")
        
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return utils.bad_request("Invalid JSON body")
        
    name = (payload.get("name") or "").strip()
    if not name:
        return utils.bad_request("'name' is required")
        
    content_type = payload.get("content_type", "").strip()
    if not content_type:
        return utils.bad_request("'content_type' is required")
        
    # Validate content type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if content_type not in allowed_types:
        return utils.bad_request(f"Content type must be one of: {', '.join(allowed_types)}")
        
    size_bytes = int(payload.get("size_bytes", 0))
    if size_bytes <= 0:
        return utils.bad_request("'size_bytes' must be greater than 0")
        
    # Check size limit (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    if size_bytes > max_size:
        return utils.bad_request(f"File size cannot exceed {max_size} bytes")
        
    if not quota_service.can_add(user_id, size_bytes):
        return utils.bad_request("Quota exceeded")
        
    description = payload.get("description", "")
    
    try:
        result = image_service.generate_upload_url(
            user_id, album_id, name=name, description=description, 
            size_bytes=size_bytes, content_type=content_type
        )
        return utils.ok(result)
    except ValidationError as e:
        return utils.bad_request(str(e))


def confirm_upload(event, context):  # POST /albums/{album_id}/images/{image_id}/confirm
    user_id = utils.get_user_id(event)
    params = event.get("pathParameters", {})
    album_id = params.get("album_id")
    image_id = params.get("image_id")
    if not (album_id and image_id):
        return utils.bad_request("album_id or image_id missing")
    
    # Validate ownership first
    existing_image = image_service.get_image(user_id, album_id, image_id)
    if not existing_image:
        return utils.unauthorized("User does not own the image")
        
    image = image_service.confirm_upload(user_id, album_id, image_id)
    if not image:
        return utils.not_found("Image supposed to be uploaded was not found")
        
    # Add to quota on successful confirmation
    quota_service.add_usage(user_id, image["size_bytes"])
    return utils.ok(image)


def get_image(event, context):  # GET /albums/{album_id}/images/{image_id}
    user_id = utils.get_user_id(event)
    params = event.get("pathParameters", {})
    album_id = params.get("album_id")
    image_id = params.get("image_id")
    if not (album_id and image_id):
        return utils.bad_request("album_id or image_id missing")
    image = image_service.get_image(user_id, album_id, image_id)
    if not image:
        return utils.unauthorized("User does not own the image")
    return utils.ok(image)


def update_image(event, context):  # PUT /albums/{album_id}/images/{image_id}
    user_id = utils.get_user_id(event)
    params = event.get("pathParameters", {})
    album_id = params.get("album_id")
    image_id = params.get("image_id")
    if not (album_id and image_id):
        return utils.bad_request("album_id or image_id missing")
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return utils.bad_request("Invalid JSON body")
    try:
        image = image_service.update_image(user_id, album_id, image_id, name=payload.get("name"), description=payload.get("description"))
    except ValidationError as e:
        return utils.bad_request(str(e))
    if not image:
        return utils.unauthorized("User does not own the image")
    return utils.ok(image)


def generate_download_url(event, context):  # GET /albums/{album_id}/images/{image_id}/download-url
    user_id = utils.get_user_id(event)
    params = event.get("pathParameters", {})
    album_id = params.get("album_id")
    image_id = params.get("image_id")
    if not (album_id and image_id):
        return utils.bad_request("album_id or image_id missing")
        
    result = image_service.generate_download_url(user_id, album_id, image_id)
    if not result:
        return utils.unauthorized("User does not own the image")
        
    return utils.ok(result)


def delete_image(event, context):  # DELETE /albums/{album_id}/images/{image_id}
    user_id = utils.get_user_id(event)
    params = event.get("pathParameters", {})
    album_id = params.get("album_id")
    image_id = params.get("image_id")
    if not (album_id and image_id):
        return utils.bad_request("album_id or image_id missing")
    # Adjust quota if size known
    existing = image_service.get_image(user_id, album_id, image_id)
    deleted = image_service.delete_image(user_id, album_id, image_id)
    if not deleted:
        return utils.unauthorized("User does not own the image")
    # Only subtract usage for active images
    if existing and existing.get("size_bytes") and existing.get("status") == "active":
        quota_service.subtract_usage(user_id, existing["size_bytes"])
    return utils.ok({"deleted": True})
