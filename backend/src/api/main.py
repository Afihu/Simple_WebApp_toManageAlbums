"""Main Lambda handler dispatching to specific endpoint handlers.

This is a lightweight router interpreting HTTP API (v2) events.
"""
import re

from typing import Callable, Tuple, Optional

from . import albums, images, quota, utils


RouteHandler = Callable[[dict, object], dict]


ROUTES: list[Tuple[str, str, RouteHandler]] = [
    ("GET", r"^/albums$", albums.list_albums),
    ("POST", r"^/albums$", albums.create_album),
    ("GET", r"^/albums/(?P<album_id>[^/]+)$", albums.get_album),
    ("PUT", r"^/albums/(?P<album_id>[^/]+)$", albums.update_album),
    ("DELETE", r"^/albums/(?P<album_id>[^/]+)$", albums.delete_album),
    ("POST", r"^/albums/(?P<album_id>[^/]+)/images/upload-url$", images.generate_upload_url),
    ("POST", r"^/albums/(?P<album_id>[^/]+)/images/(?P<image_id>[^/]+)/confirm$", images.confirm_upload),
    ("GET", r"^/albums/(?P<album_id>[^/]+)/images/(?P<image_id>[^/]+)$", images.get_image),
    ("PUT", r"^/albums/(?P<album_id>[^/]+)/images/(?P<image_id>[^/]+)$", images.update_image),
    ("DELETE", r"^/albums/(?P<album_id>[^/]+)/images/(?P<image_id>[^/]+)$", images.delete_image),
    ("GET", r"^/albums/(?P<album_id>[^/]+)/images/(?P<image_id>[^/]+)/download-url$", images.generate_download_url),
    ("GET", r"^/quota$", quota.get_quota),
]


def handler(event, context):  # AWS Lambda entrypoint
    method = event.get("requestContext", {}).get("http", {}).get("method") or event.get("httpMethod")
    raw_path = event.get("rawPath") or event.get("path") or ""

    # Handle CORS preflight requests
    if method == "OPTIONS":
        return utils.handle_options()

    for m, pattern, fn in ROUTES:
        if m == method:
            match = re.match(pattern, raw_path)
            if match:
                # Update path parameters with captured groups
                if event.get("pathParameters") is None:
                    event["pathParameters"] = {}
                event["pathParameters"].update(match.groupdict())
                return fn(event, context)

    return utils.not_found("Route not found")
