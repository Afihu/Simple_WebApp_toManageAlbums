class Quota:
    def __init__(self, user_id: str, total_storage_bytes: int = 0, album_count: int = 0):
        self.user_id = user_id
        self.total_storage_bytes = total_storage_bytes
        self.album_count = album_count

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "total_storage_bytes": self.total_storage_bytes,
            "album_count": self.album_count,
        }
