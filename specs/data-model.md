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
| album_id    | UUID      | Unique identifier for the album             |
| user_id     | string    | Owner's Cognito user ID                     |
| name        | string    | Album name (max 100 chars, safe chars only) |
| description | string    | Album description (optional)                |
| image_count | integer   | Number of images in the album               |
| created_at  | datetime  | Creation timestamp                          |
| updated_at  | datetime  | Last updated timestamp                      |



## Image
| Field        | Type      | Description                                 |
|--------------|-----------|---------------------------------------------|
| image_id     | UUID      | Unique identifier for the image             |
| album_id     | string    | Album this image belongs to                 |
| user_id      | string    | Owner's Cognito user ID                     |
| name         | string    | Image name (max 100 chars, safe chars only) |
| description  | string    | Image description (optional)                |
| s3_key       | string    | S3 object key for the image file            |
| size_bytes   | integer   | File size in bytes                          |
| content_type | string    | MIME type (e.g., image/jpeg)                |
| status       | string    | Upload status: 'pending' or 'active'        |
| created_at   | datetime  | Upload timestamp                            |
| updated_at   | datetime  | Last updated timestamp                      |



## Storage Quota (per user)
| Field               | Type    | Description                                 |
|---------------------|---------|---------------------------------------------|
| user_id             | string  | Cognito user ID                             |
| total_storage_bytes | integer | Total storage used by the user (in bytes)   |
| album_count         | integer | Number of albums owned by the user          |


### Example of Presigned URL Generation and DynamoDB entry
```python
# Example presigned URL generation for image upload
import boto3
from datetime import datetime, timedelta
import uuid

# Initialize the S3 client
s3_client = boto3.client('s3', region_name='ap-southeast-1')

# Generate unique image ID and S3 key
image_id = str(uuid.uuid4())
s3_key = f'{user_id}/{album_id}/{image_id}'

# Generate presigned URL for upload (expires in 15 minutes)
upload_url = s3_client.generate_presigned_url(
    'put_object',
    Params={
        'Bucket': 'my-albums-and-images-bucket',
        'Key': s3_key,
        'ContentType': event['content_type']
    },
    ExpiresIn=900  # 15 minutes
)

# Create pending image record in DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table('AlbumsApp')
now = datetime.utcnow().isoformat()

table.put_item(
    Item={
        'user_id': user_id,  # Partition key
        'type': f'image#{image_id}',  # Sort key
        'image_id': image_id,
        'album_id': album_id,
        'user_id': user_id,
        'name': event['name'],
        'description': event.get('description', ''),
        's3_key': s3_key,
        'size_bytes': event['size_bytes'],
        'content_type': event['content_type'],
        'status': 'pending',  # Will be updated to 'active' after upload confirmation
        'created_at': now,
        'updated_at': now
    }
)

# Return presigned URL and image metadata
return {
    'upload_url': upload_url,
    'image_id': image_id,
    'expires_in': 900
}

# Example presigned URL generation for image download
def generate_download_url(user_id, album_id, image_id):
    # Retrieve image metadata from DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('AlbumsApp')
    
    response = table.get_item(
        Key={
            'user_id': user_id,
            'type': f'image#{image_id}'
        }
    )
    
    if 'Item' not in response or response['Item']['status'] != 'active':
        raise ValueError("Image not found or not ready")
    
    image_data = response['Item']
    
    # Generate presigned URL for download (expires in 15 minutes)
    s3_client = boto3.client('s3', region_name='ap-southeast-1')
    download_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': 'my-albums-and-images-bucket',
            'Key': image_data['s3_key']
        },
        ExpiresIn=900  # 15 minutes
    )
    
    return {
        'download_url': download_url,
        'expires_in': 900,
        'content_type': image_data['content_type'],
        'size_bytes': image_data['size_bytes']
    }
```
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
