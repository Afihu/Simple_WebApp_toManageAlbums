class Quota:
    def __init__(self, user_id: str, max_bytes: int, used_bytes: int = 0):
        self.user_id = user_id
        self.max_bytes = max_bytes
        self.used_bytes = used_bytes

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "max_bytes": self.max_bytes,
            "used_bytes": self.used_bytes,
        }
