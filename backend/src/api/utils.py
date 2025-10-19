import json
import base64
import os
from typing import Any, Dict, Optional
import boto3
from datetime import datetime
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def _resp(status: int, body: Dict[str, Any]):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Allow CORS for frontend
            "Access-Control-Allow-Headers": "Content-Type,Authorization,x-user-id",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def ok(body: Dict[str, Any]):
    return _resp(200, body)


def created(body: Dict[str, Any]):
    return _resp(201, body)


def not_found(message: str = "Not found"):
    return _resp(404, {"error": "NotFound", "message": message})


def bad_request(message: str):
    return _resp(400, {"error": "BadRequest", "message": message})


def server_error(message: str = "Internal server error"):
    return _resp(500, {"error": "ServerError", "message": message})


def unauthorized(message: str = "Unauthorized"):
    return _resp(401, {"error": "Unauthorized", "message": message})


def handle_options():
    """Handle CORS preflight requests."""
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,x-user-id",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": ""
    }


def get_user_id(event):
    """Extract user_id from JWT token and ensure user exists in DynamoDB.
    
    This implements the 2-layer authentication from System_flow.md:
    1. JWT validation (handled by API Gateway Cognito Authorizer)
    2. User existence check in DynamoDB (handled here)
    
    For development/testing, falls back to x-user-id header.
    """
    headers = event.get("headers") or {}
    
    # Development fallback - use x-user-id header if present
    test_user_id = headers.get("x-user-id")
    if test_user_id:
        return test_user_id
    
    # Production: Extract user_id from JWT token
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # This should not happen if API Gateway Cognito Authorizer is working
        return "anonymous-user"
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    try:
        # Decode JWT payload (API Gateway already validated signature)
        # JWT format: header.payload.signature
        payload_encoded = token.split(".")[1]
        # Add padding if needed for base64 decoding
        payload_encoded += "=" * (4 - len(payload_encoded) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        user_id = payload.get("sub")
        if not user_id:
            return "anonymous-user"
        
        # Ensure user exists in DynamoDB, create if not
        _ensure_user_exists(user_id)
        return user_id
        
    except (IndexError, ValueError, json.JSONDecodeError):
        # Invalid JWT format - fallback
        return "anonymous-user"


def _ensure_user_exists(user_id: str):
    """Ensure user quota record exists in DynamoDB, create with defaults if not."""
    try:
        table_name = os.getenv("DYNAMODB_TABLE", "AlbumsApp")
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)
        
        # Check if user quota exists
        response = table.get_item(
            Key={
                "user_id": user_id,
                "type": "quota"
            }
        )
        
        # If not exists, create default quota
        if "Item" not in response:
            now = datetime.utcnow().isoformat()
            table.put_item(
                Item={
                    "user_id": user_id,
                    "type": "quota",
                    "total_storage_bytes": 0,
                    "album_count": 0,
                    "created_at": now,
                    "updated_at": now
                }
            )
    except Exception:
        # Ignore errors to prevent blocking requests
        # Quota service will handle missing records gracefully
        pass
