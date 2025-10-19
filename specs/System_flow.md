<!-- This file documents how the system is INTENDED to work -->
# Client
- The client (frontend SPA) will have user sign-up/login via the hosted Cognito UI.
- After login, the client will receive an authorization code which it makes a POST request to Cognito's token endpoint to exchange for tokens (ID token, access token, refresh token).
- When making API requests, the client includes the ID token in the `Authorization` header as a Bearer token.

# API Gateway
- API Gateway will have a Cognito User Pool Authorizer configured to validate incoming requests (using the ID token).
    - If the token is valid, API Gateway (acting as a proxy) forwards the request as a full event to the appropriate Lambda function.
    - If the token is invalid or missing, API Gateway returns a 401 Unauthorized response.
- The API endpoints defined in `API_contracts.md` will be set up in API Gateway, but all point to a single Lambda function (the backend) which will handle routing internally.
    - The Gateway is as proxy to pass the event fully to the Lambda function, so the Lambda can have full context of the request (e.g., path, method, headers, body).

## Authentication
- The system has 2 authentication layers:
    1. Cognito User Pool Authorizer in API Gateway (validates JWT token) - providing user with access to the APIs.
    2. Custom authentication in the Lambda function (validates user existence in DynamoDB) - ensuring user is initialized in the system or owning the resource they are trying to access.
    
# Lambda Function (backend)
## Entry Point & Routing
- The Lambda function has an entry point (`main.py`) which routes requests to different handlers based on the HTTP method and path.
    -  This router would be responsible for decdoding the JWT token and extracting user information (e.g., `sub` claim as `user_id`).
    -  After getting the `user_id`, it would check that against the DynamoDB table to ensure the user exists.
        - If yes, the request is processed further.
        - If no, the user is initialized (with the set limited of storage usage) and added to the DynamoDB table then the request is processed.
- Each handler function implements the business logic for the corresponding API endpoint (e.g., create album, upload image).

## Albums Handler
- **GET /albums**:
    - Receives the request and `user_id` from router, queries DynamoDB for all albums belonging to the user, and receives the list of `album_ids` and their metadata.
    - It would then invoke the S3 service to generate pre-signed URLs for each album's first 4 images AT MOST (if any) to create the thumbnails. **Note** that there are already a service from the *images handler* that carries out this task, so the *albums handler* would call that service instead of implementing it again.
    - Finally, it returns the list of albums with their metadata and pre-signed URLs to the client with a 200 OK status.

- **POST /albums**:
    - Receives the request body (album name, description) and `user_id` from router.
    - Validates the input based on the existing constraints in `plan.m` (return 403 Forbidden if invalid), generates a new `album_id`, and creates a new album item in DynamoDB with initial metadata (e.g., `image_count` = 0).
    - Updates the user's quota (increment album count).
    - Returns the created album's metadata to the client with a 201 Created status.

- **GET /albums/{album_id}**:
    - Receives the request and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` exists.
    - If yes, it receives the album's metadata.
        - It would then check if the respective entries of `user_id` + `album_id` + `image_id` exist in the images table, and if so, invoke the S3 service to generate a pre-signed URL for each image in the album (if any). **Note** that there are already a service from the *images handler* that carries out this task, so the *albums handler* would call that service instead of implementing it again.
        - Finally, it returns the album's metadata, images' metadata and pre-signed URLs to the client with a 200 OK status.
    - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the album.

- **PUT /albums/{album_id}**:
    - Receives the request body (updated album name, description) and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` exists.
    - Validates the input based on the existing constraints in `plan.md` (return 403 Forbidden if invalid).
    - If yes, it updates the album item in DynamoDB with the new metadata and returns the updated album's metadata to the client with a 200 OK status.
    - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the album.

- **DELETE /albums/{album_id}**:
    - Receives the request and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` exists.
    - If yes, it queries DynamoDB for all images in the album to get their `s3_key`s.
        - It would then invoke the S3 service to delete all images in the album from S3.
        - After that, it deletes all image items in DynamoDB associated with the album, then deletes the album item itself.
        - Finally, it updates the user's quota (decrement album count) and returns a success response to the client with a 200 OK status.
    - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the album.

## Images Handler
- **GET /albums/{album_id}/images**:
    - Will be removed as it is overlapping with **GET /albums/{album_id}** in the *albums handler*.

- **POST /albums/{album_id}/images/upload-url**:
    - Receives the request body (image name, description, content type, size in bytes) and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` exists.
    - If yes, it validates the input based on the existing constraints in `plan.md` (return 403 Forbidden if invalid), generates a new `image_id` and new `s3_key`, and creates a new image item in DynamoDB with initial metadata (e.g., `status` = 'pending').
        - It would then invoke the S3 service to generate a pre-signed URL for uploading the image to S3.
        - Finally, it returns the pre-signed URL and `image_id` to the client with a 200 OK status.
    - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the album.

- **POST /albums/{album_id}/images/{image_id}/confirm**:
    - Receives the request and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` + `image_id` exists.
    - If yes, it then check if the S3 object exists (to confirm the upload was successful).
        - If the S3 object exists, it updates the image item in DynamoDB to set `status` = 'active'.
            - It then updates the album's `image_count` and the user's storage quota accordingly.
            - It would then invoke the S3 service to generate a pre-signed URL for displaying the new image.
            - Finally, it returns the updated image's metadata to the client with a 201 Created status and pre-signed URL.
        - If the S3 object does not exist, it returns a 404 Not Found error to the client, stating that the image supposed to be uploaded was not found.
    - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the image.

- **GET /albums/{album_id}/images/{image_id}**:
    - Receives the request and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` + `image_id` exists.
        - If yes, it retrieves the image's metadata from DynamoDB then return the metadata to the client with a 200 OK status.
        - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the image. 

- **PUT /albums/{album_id}/images/{image_id}**:
    - Receives the request body (updated image name, description) and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` + `image_id` exists.
        - Validates the input based on the existing constraints in `plan.md` (return 403 Forbidden if invalid).
        - If yes, it updates the image item in DynamoDB with the new metadata and returns the updated image's metadata to the client with a 200 OK status.
        - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the image.

- **DELETE /albums/{album_id}/images/{image_id}**:
    - Receives the request and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` + `image_id` exists.
        - If yes, it retrieves the image's `s3_key` from DynamoDB.
            - It would then invoke the S3 service to delete the image from S3.
            - After that, it deletes the image item in DynamoDB.
            - Finally, it updates the album's `image_count` and the user's storage quota accordingly, then returns a success response to the client with a 200 OK status.
        - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the image.

- **GET /albums/{album_id}/images/{image_id}/download-url**:
    - This service would be also be called by the *albums handler* when it needs to generate pre-signed URLs for images display.
    - Receives the request and `user_id` from router, queries DynamoDB if the entry of `user_id` + `album_id` + `image_id` exists.
        - If yes, it retrieves the image's metadata from DynamoDB.
            - It would then invoke the S3 service to generate a pre-signed URL for downloading the image from S3.
            - Finally, it returns the pre-signed URL to the client with a 200 OK status.
        - If no, it returns a 401 Unauthorized error to the client, stating that the user does not own the image.