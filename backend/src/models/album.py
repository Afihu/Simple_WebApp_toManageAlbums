from typing import Optional
from datetime import datetime

class Album:
    def __init__(self, album_id: str, user_id: str, name: str, description: Optional[str] = None, created_at: Optional[str] = None):
        self.album_id = album_id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "album_id": self.album_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }
