"""Lambda handlers for /albums endpoints (tasks T026-T030).

Routing to these handlers will be done by the main dispatcher.
"""
import json
from typing import Any, Dict

from ..services.album_service import AlbumService
from ..services.image_service import ImageService
from ..services.validation import ValidationError
from . import utils

album_service = AlbumService()
image_service = ImageService()


def list_albums(event, context):  # GET /albums
    user_id = utils.get_user_id(event)
    albums = album_service.list_albums(user_id)
    
    # Add pre-signed URLs for first 4 images of each album
    for album in albums:
        album_id = album.get("album_id")
        if album_id:
            # Get first 4 images for thumbnails
            images = image_service.list_images(user_id, album_id, include_pending=False)
            thumbnail_urls = []
            
            for image in images[:4]:  # First 4 images only
                image_id = image.get("image_id")
                if image_id:
                    download_result = image_service.generate_download_url(user_id, album_id, image_id)
                    if download_result:
                        thumbnail_urls.append({
                            "image_id": image_id,
                            "download_url": download_result["download_url"],
                            "expires_in": download_result["expires_in"]
                        })
            
            album["thumbnail_urls"] = thumbnail_urls
    
    return utils.ok({"items": albums})


def create_album(event, context):  # POST /albums
    user_id = utils.get_user_id(event)
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return utils.bad_request("Invalid JSON body")
    name = (payload.get("name") or "").strip()
    if not name:
        return utils.bad_request("'name' is required")
    description = payload.get("description")
    try:
        album = album_service.create_album(user_id, name=name, description=description)
    except ValidationError as e:
        return utils.bad_request(str(e))
    return utils.created(album)


def get_album(event, context):  # GET /albums/{album_id}
    user_id = utils.get_user_id(event)
    album_id = event.get("pathParameters", {}).get("album_id")
    if not album_id:
        return utils.bad_request("album_id missing")
    
    album = album_service.get_album(user_id, album_id)
    if not album:
        return utils.unauthorized("User does not own the album")
    
    # Get all images in the album with pre-signed URLs
    images = image_service.list_images(user_id, album_id, include_pending=False)
    images_with_urls = []
    
    for image in images:
        image_id = image.get("image_id")
        if image_id:
            download_result = image_service.generate_download_url(user_id, album_id, image_id)
            if download_result:
                image_with_url = image.copy()
                image_with_url["download_url"] = download_result["download_url"]
                image_with_url["expires_in"] = download_result["expires_in"]
                images_with_urls.append(image_with_url)
    
    return utils.ok({
        "album": album,
        "images": images_with_urls
    })


def update_album(event, context):  # PUT /albums/{album_id}
    user_id = utils.get_user_id(event)
    album_id = event.get("pathParameters", {}).get("album_id")
    if not album_id:
        return utils.bad_request("album_id missing")
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return utils.bad_request("Invalid JSON body")
    try:
        album = album_service.update_album(user_id, album_id, name=payload.get("name"), description=payload.get("description"))
    except ValidationError as e:
        return utils.bad_request(str(e))
    if not album:
        return utils.unauthorized("User does not own the album")
    return utils.ok(album)


def delete_album(event, context):  # DELETE /albums/{album_id}
    user_id = utils.get_user_id(event)
    album_id = event.get("pathParameters", {}).get("album_id")
    if not album_id:
        return utils.bad_request("album_id missing")
    
    # Check if album exists (ownership validation)
    album = album_service.get_album(user_id, album_id)
    if not album:
        return utils.unauthorized("User does not own the album")
    
    # Get all images in album to delete from S3
    images = image_service.list_images(user_id, album_id, include_pending=True)
    
    # Delete all images first
    for image in images:
        image_id = image.get("image_id")
        if image_id:
            image_service.delete_image(user_id, album_id, image_id)
    
    # Delete the album itself
    deleted = album_service.delete_album(user_id, album_id)
    if not deleted:
        return utils.server_error("Failed to delete album")
    
    # Note: User quota will be updated by image deletion in image_service
    return utils.ok({"deleted": True})
