from typing import Optional
from datetime import datetime


class Image:
    def __init__(
        self,
        image_id: str,
        album_id: str,
        user_id: str,
        name: str,
        s3_key: str,
        description: Optional[str] = None,
        size_bytes: Optional[int] = None,
        content_type: Optional[str] = None,
        status: str = "active",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.image_id = image_id
        self.album_id = album_id
        self.user_id = user_id
        self.name = name
        self.s3_key = s3_key
        self.description = description
        self.size_bytes = size_bytes
        self.content_type = content_type
        self.status = status  # 'pending' or 'active'
        now = datetime.utcnow().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "album_id": self.album_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "s3_key": self.s3_key,
            "size_bytes": self.size_bytes,
            "content_type": self.content_type,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
