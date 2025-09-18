provider "aws" {
  access_key = "test"
  secret_key = "test"
  region     = "us-east-1"
  s3_force_path_style = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    s3 = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    lambda = "http://localhost:4566"
    cloudfront = "http://localhost:4566"
  }
}

resource "aws_s3_bucket" "images" {
  bucket = "albumsapp-images"
}

resource "aws_s3_bucket" "frontend" {
  bucket = "albumsapp-frontend"
}

resource "aws_dynamodb_table" "albumsapp" {
  name           = "AlbumsApp"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "type"

  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "type"
    type = "S"
  }
}

resource "aws_lambda_function" "albums_lambda" {
  function_name = "albums-lambda"
  handler       = "main.handler"
  runtime       = "python3.13"
  role          = "arn:aws:iam::000000000000:role/lambda-role"
  filename      = "backend/dist/albums-lambda.zip"
  source_code_hash = filebase64sha256("backend/dist/albums-lambda.zip")
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.albumsapp.name
      IMAGES_BUCKET  = aws_s3_bucket.images.bucket
      FRONTEND_BUCKET = aws_s3_bucket.frontend.bucket
    }
  }
}

resource "aws_cloudfront_distribution" "frontend_cdn" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "frontendS3Origin"
  }
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "frontendS3Origin"
    viewer_protocol_policy = "allow-all"
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
