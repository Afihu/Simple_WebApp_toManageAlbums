from typing import Optional
from datetime import datetime

class Image:
    def __init__(self, image_id: str, album_id: str, user_id: str, name: str, s3_key: str, description: Optional[str] = None, size: Optional[int] = None, created_at: Optional[str] = None):
        self.image_id = image_id
        self.album_id = album_id
        self.user_id = user_id
        self.name = name
        self.s3_key = s3_key
        self.description = description
        self.size = size
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "album_id": self.album_id,
            "user_id": self.user_id,
            "name": self.name,
            "s3_key": self.s3_key,
            "description": self.description,
            "size": self.size,
            "created_at": self.created_at,
        }
