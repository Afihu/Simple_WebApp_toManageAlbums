# Data Model: Web App to Manage Albums

**Branch**: `001-system-design` | **Date**: September 17, 2025 | [**Spec**](specs/spec.md) | [**Plan**](specs/plan.md)

**Input**: Feature specification from `/specs/spec.md` and Initial system design plan from `/specs/plan.md`



## Summary
This document defines the foundational data models for the Albums web app, based on the current specification and implementation plan. These models will be used for validation, storage, and API contracts.



## User
| Field     | Type    | Description                                      |
|-----------|---------|--------------------------------------------------|
| user_id   | string  | Unique identifier from Cognito (the `sub` claim) |
| username  | string  | Display name (optional, from Cognito)            |



## Album
| Field       | Type      | Description                                 |
|-------------|-----------|---------------------------------------------|
| album_id    | string    | Unique identifier for the album             |
| user_id     | string    | Owner's Cognito user ID                     |
| name        | string    | Album name (max 100 chars, safe chars only) |
| description | string    | Album description (optional)                |
| created_at  | datetime  | Creation timestamp                          |
| updated_at  | datetime  | Last updated timestamp                      |



## Image
| Field        | Type      | Description                                 |
|--------------|-----------|---------------------------------------------|
| image_id     | string    | Unique identifier for the image             |
| album_id     | string    | Album this image belongs to                 |
| user_id      | string    | Owner's Cognito user ID                     |
| name         | string    | Image name (max 100 chars, safe chars only) |
| description  | string    | Image description (optional)                |
| s3_key       | string    | S3 object key for the image file            |
| size_bytes   | integer   | File size in bytes                          |
| content_type | string    | MIME type (e.g., image/jpeg)                |
| created_at   | datetime  | Upload timestamp                            |
| updated_at   | datetime  | Last updated timestamp                      |



## Storage Quota (per user)
| Field               | Type    | Description                                 |
|---------------------|---------|---------------------------------------------|
| user_id             | string  | Cognito user ID                             |
| total_storage_bytes | integer | Total storage used by the user (in bytes)   |
| album_count         | integer | Number of albums owned by the user          |



### Example of a Cognito Token

Below is a sample Cognito ID token (JWT) returned after a user logs in. The token is a single string, but here it's split for clarity:

```
eyJraWQiOiJLT1p5b2p3a1Z... (header)
.
eyJzdWIiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhbGljZSIsImVtYWlsIjoiYWxpY2VAZXhhbXBsZS5jb20iLCJhdWQiOiIxYWJjZGVmZ2hpamtsbW5vcHFycyIsImlzcyI6Imh0dHBzOi8vY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb20vdXMtZWFzdC0xX2V4YW1wbGUiLCJleHAiOjE2OTQ5ODg0MDAsImlhdCI6MTY5NDk4NDgwMH0
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### Decoded Header (base64url):
```json
{
	"kid": "KOZyojwkVK...",
	"alg": "RS256"
}
```

#### Decoded Payload (base64url):
```json
{
	"sub": "1234567890",           // Unique user ID (use this as user_id)
	"username": "alice",
	"email": "alice@example.com",
	"aud": "1abcdefgijklmnopqrs",  // App client ID
	"iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example",
	"exp": 1694988400,              // Expiration time (changes every login)
	"iat": 1694984800               // Issued at
}
```

#### Signature
The third part is a cryptographic signature. It changes every time and is used to verify the token's authenticity.

**Note:** The `sub` field is the unique, stable identifier for the user. Other fields like `exp` and the signature will change with each login or token refresh.

## Notes
- All string fields for names should be validated for length and allowed characters.
- Timestamps are in UTC.
- S3 keys should be structured to include the user_id for easy lookup and access control.
- These models are a starting point and can be expanded as needed.
