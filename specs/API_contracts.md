# API Contracts: Web App to Manage Albums

**Branch**: `001-system-design` | **Date**: September 17, 2025

This document defines the REST API endpoints for the Albums web app, based on the current data model, feature specification, and implementation plan. It serves as the contract between frontend and backend, and as a reference for implementation and testing.

---

## Authentication
- All endpoints (except login) require a valid AWS Cognito JWT in the `Authorization` header: `Bearer <token>`
- The `sub` claim from the token is used as the user's unique ID

---

## Endpoints

### Album Endpoints

| Method | Path                | Description                | Request Body         | Response Body         | Notes |
|--------|---------------------|----------------------------|----------------------|-----------------------|-------|
| GET    | /albums             | List all albums for user   | —                    | `[Album]`             | Auth required |
| POST   | /albums             | Create a new album         | `{name, description}`| `Album`               | Auth required |
| GET    | /albums/{album_id}  | Get album details          | —                    | `Album`               | Auth required, must own album |
| PUT    | /albums/{album_id}  | Update album details       | `{name, description}`| `Album`               | Auth required, must own album |
| DELETE | /albums/{album_id}  | Delete album (and images)  | —                    | `{success: true}`     | Auth required, must own album |

### Image Endpoints

| Method | Path                              | Description                | Request Body         | Response Body         | Notes |
|--------|-----------------------------------|----------------------------|----------------------|-----------------------|-------|
| GET    | /albums/{album_id}/images         | List images in album       | —                    | `[Image]`             | Auth required, must own album |
| POST   | /albums/{album_id}/images         | Upload new image           | multipart/form-data  | `Image`               | Auth required, must own album, enforce size/type limits |
| GET    | /albums/{album_id}/images/{image_id} | Get image metadata      | —                    | `Image`               | Auth required, must own album/image |
| PUT    | /albums/{album_id}/images/{image_id} | Update image metadata   | `{name, description}`| `Image`               | Auth required, must own album/image |
| DELETE | /albums/{album_id}/images/{image_id} | Delete image            | —                    | `{success: true}`     | Auth required, must own album/image |

### Quota Endpoint

| Method | Path         | Description                | Request Body | Response Body         | Notes |
|--------|--------------|----------------------------|--------------|-----------------------|-------|
| GET    | /quota       | Get user's storage quota   | —            | `StorageQuota`        | Auth required |

---

## Data Schemas

### Album
```json
{
  "album_id": "string",
  "user_id": "string",
  "name": "string",
  "description": "string",
  "image_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Image
```json
{
  "image_id": "string",
  "album_id": "string",
  "user_id": "string",
  "name": "string",
  "description": "string",
  "s3_key": "string",
  "size_bytes": 12345,
  "content_type": "image/jpeg",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### StorageQuota
```json
{
  "user_id": "string",
  "total_storage_bytes": 123456,
  "album_count": 3
}
```

---

## Error Responses
- All errors return JSON with an `error` field and a `message` field.
- Example:
```json
{
  "status": 401,
  "error": "Unauthorized",
  "message": "Missing or invalid token."
}
```

---

## Notes
- All endpoints require authentication unless otherwise noted.
- All IDs are strings (UUIDs or similar).
- Timestamps are in ISO 8601 UTC format.
- File uploads must enforce size and type limits as described in the spec.
- Only the owner of an album or image can access or modify it.

---

*Update this file as the design evolves or as implementation details are finalized.*
