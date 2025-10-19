"""QuotaService - DynamoDB based implementation.

Stores a single item per user with key (user_id, 'quota').
Tracks total_storage_bytes and album_count. Enforces a soft cap via env var.
"""
from __future__ import annotations
import os
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

from ..models.quota import Quota

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "AlbumsApp")
DEFAULT_MAX_BYTES = int(os.getenv("DEFAULT_MAX_BYTES", str(500 * 1024 * 1024)))  # 500MB default


class QuotaService:
    def __init__(self, dynamodb_resource=None):
        self.dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(TABLE_NAME)

    @staticmethod
    def _quota_sort_key() -> str:
        return "quota"

    # PK/SK pattern:
    #   PK: user_id
    #   SK: type = 'quota'
    # Single item per user tracking aggregate usage and album count.

    def _get_item(self, user_id: str) -> Dict[str, Any]:
        resp = self.table.get_item(Key={"user_id": user_id, "type": self._quota_sort_key()})
        return resp.get("Item") or {}

    def _ensure(self, user_id: str) -> Dict[str, Any]:
        item = self._get_item(user_id)
        if not item:
            quota = Quota(user_id=user_id, total_storage_bytes=0, album_count=0)
            item = {
                "user_id": user_id,
                "type": self._quota_sort_key(),
                **quota.to_dict(),
            }
            self.table.put_item(Item=item)
        return item

    def get_quota(self, user_id: str) -> Dict:
        return self._ensure(user_id)

    def add_usage(self, user_id: str, bytes_added: int) -> None:
        self.table.update_item(
            Key={"user_id": user_id, "type": self._quota_sort_key()},
            UpdateExpression="ADD total_storage_bytes :b",
            ExpressionAttributeValues={":b": bytes_added},
        )

    def subtract_usage(self, user_id: str, bytes_removed: int) -> None:
        # Use a two-step to avoid negative values
        quota = self._ensure(user_id)
        new_value = max(0, quota.get("total_storage_bytes", 0) - bytes_removed)
        self.table.update_item(
            Key={"user_id": user_id, "type": self._quota_sort_key()},
            UpdateExpression="SET total_storage_bytes = :v",
            ExpressionAttributeValues={":v": new_value},
        )

    def can_add(self, user_id: str, size: int) -> bool:
        quota = self._ensure(user_id)
        return quota.get("total_storage_bytes", 0) + size <= DEFAULT_MAX_BYTES

