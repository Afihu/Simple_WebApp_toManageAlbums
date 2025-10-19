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
| GET    | /albums             | List all albums for user   | —                    | `{items: [AlbumWithThumbnails]}`  | Auth required |
| POST   | /albums             | Create a new album         | `{name, description}`| `Album`               | Auth required |
| GET    | /albums/{album_id}  | Get album details with images | —                 | `{album: Album, images: [ImageWithURL]}` | Auth required, returns 401 if user doesn't own album |
| PUT    | /albums/{album_id}  | Update album details       | `{name, description}`| `Album`               | Auth required, returns 401 if user doesn't own album |
| DELETE | /albums/{album_id}  | Delete album (and images)  | —                    | `{deleted: true}`     | Auth required, returns 401 if user doesn't own album |

### Image Endpoints

| Method | Path                                         | Description                | Request Body         | Response Body         | Notes |
|--------|----------------------------------------------|----------------------------|----------------------|-----------------------|-------|
| POST   | /albums/{album_id}/images/upload-url         | Get presigned URL for image upload | `{name, description, content_type, size_bytes}` | `{upload_url, image_id}` | Auth required, returns 401 if user doesn't own album |
| POST   | /albums/{album_id}/images/{image_id}/confirm | Confirm image upload completion | — | `Image` | Auth required, returns 401 if user doesn't own image, returns 404 if S3 object not found |
| GET    | /albums/{album_id}/images/{image_id}         | Get image metadata      | —                    | `Image`               | Auth required, returns 401 if user doesn't own image |
| PUT    | /albums/{album_id}/images/{image_id}         | Update image metadata   | `{name, description}`| `Image`               | Auth required, returns 401 if user doesn't own image |
| DELETE | /albums/{album_id}/images/{image_id}         | Delete image            | —                    | `{deleted: true}`     | Auth required, returns 401 if user doesn't own image |
| GET    | /albums/{album_id}/images/{image_id}/download-url | Get presigned URL for image download | — | `{download_url}` | Auth required, returns 401 if user doesn't own image |

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
  "status": "active",
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

### AlbumWithThumbnails (GET /albums response)
```json
{
  "album_id": "string",
  "user_id": "string", 
  "name": "string",
  "description": "string",
  "image_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "thumbnail_urls": [
    {
      "image_id": "string",
      "download_url": "string", 
      "expires_in": 900
    }
  ]
}
```

### ImageWithURL (GET /albums/{album_id} response)
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
  "status": "active",
  "created_at": "datetime",
  "updated_at": "datetime",
  "download_url": "string",
  "expires_in": 900
}
```

---

## Error Responses
- All errors return JSON with an `error` field and a `message` field.
- **401 Unauthorized**: Returned when user tries to access resources they don't own
- **403 Forbidden**: Returned for validation failures (size limits, quota exceeded, etc.)
- **404 Not Found**: Returned when resources don't exist or upload confirmation fails

### Examples:
```json
{
  "status": 401,
  "error": "Unauthorized", 
  "message": "User does not own the album."
}
```

```json
{
  "status": 403,
  "error": "BadRequest",
  "message": "Quota exceeded."
}
```

---

## Image Upload Workflow
The image upload process uses presigned URLs to avoid handling large files through the Lambda backend:

1. **Request Upload URL**: Client calls `POST /albums/{album_id}/images/upload-url` with image metadata
2. **Get Presigned URL**: Backend validates request, creates image record, returns presigned S3 URL and image_id
3. **Direct S3 Upload**: Client uploads file directly to S3 using the presigned URL
4. **Confirm Upload**: Client calls `POST /albums/{album_id}/images/{image_id}/confirm` to finalize the image record
5. **Update Quota**: Backend updates user's storage quota and album image count

## Image Download Workflow
Image downloads also use presigned URLs for security and performance:

1. **Request Download URL**: Client calls `GET /albums/{album_id}/images/{image_id}/download-url`
2. **Get Presigned URL**: Backend validates ownership and returns temporary download URL
3. **Direct S3 Download**: Client downloads file directly from S3 using the presigned URL

---

## Notes
- All endpoints require authentication unless otherwise noted.
- All IDs are strings (UUIDs or similar).
- Timestamps are in ISO 8601 UTC format.
- File uploads must enforce size and type limits as described in the spec.
- Only the owner of an album or image can access or modify it.
- Presigned URLs expire after 15 minutes for security.
- Image records are created before upload but marked as "pending" until confirmed.

---

*Update this file as the design evolves or as implementation details are finalized.*
