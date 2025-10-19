from typing import Optional
from datetime import datetime


class Album:
    def __init__(
        self,
        album_id: str,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        image_count: int = 0,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.album_id = album_id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.image_count = image_count
        now = datetime.utcnow().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self):
        return {
            "album_id": self.album_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "image_count": self.image_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
