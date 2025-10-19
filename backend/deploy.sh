#!/bin/bash

# Deployment script for AlbumsAndImagesManager Lambda function
# This script:
# 1. Creates a deployment package (deployment.zip)
# 2. Verifies the zip contents
# 3. Deploys to AWS Lambda

set -e  # Exit on any error

LAMBDA_FUNCTION_NAME="AlbumsAndImagesManager"
DEPLOYMENT_FILE="deployment.zip"
SRC_DIR="src"

echo "========================================="
echo "Lambda Deployment Script"
echo "Function: $LAMBDA_FUNCTION_NAME"
echo "========================================="
echo ""

# Step 1: Clean up old deployment file
echo "[1/4] Cleaning up old deployment package..."
if [ -f "$DEPLOYMENT_FILE" ]; then
    rm "$DEPLOYMENT_FILE"
    echo "✓ Removed old $DEPLOYMENT_FILE"
else
    echo "✓ No old deployment file to remove"
fi
echo ""

# Step 2: Create new deployment package
echo "[2/4] Creating deployment package..."
if [ -f "$DEPLOYMENT_FILE" ]; then
    rm "$DEPLOYMENT_FILE"
fi

# Use PowerShell for zipping on Windows (Git Bash compatibility)
# We need to zip the src folder itself to maintain the package structure
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    powershell.exe -Command "Compress-Archive -Path '$SRC_DIR' -DestinationPath '$DEPLOYMENT_FILE' -Force"
else
    zip -r "$DEPLOYMENT_FILE" "$SRC_DIR" -x "*.pyc" -x "__pycache__/*" -x "*/__pycache__/*" > /dev/null
fi
echo "✓ Created $DEPLOYMENT_FILE"
echo ""

# Step 3: Verify zip contents
echo "[3/4] Verifying deployment package contents..."
echo "--- ZIP Contents ---"
unzip -l "$DEPLOYMENT_FILE" | grep -E "\.py$|Directory" | head -20
echo ""
ZIP_SIZE=$(du -h "$DEPLOYMENT_FILE" | cut -f1)
echo "✓ Package size: $ZIP_SIZE"
echo ""

# Step 4: Deploy to Lambda
echo "[4/4] Deploying to AWS Lambda..."
echo "Updating function: $LAMBDA_FUNCTION_NAME"

# Use PowerShell on Windows (Git Bash compatibility)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    powershell.exe -Command "aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://$DEPLOYMENT_FILE --query 'LastModified' --output text"
else
    aws lambda update-function-code \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --zip-file "fileb://$DEPLOYMENT_FILE" \
        --query 'LastModified' \
        --output text
fi

DEPLOY_EXIT_CODE=$?

if [ $DEPLOY_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ Deployment successful!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "  - Test your Lambda function"
    echo "  - Check CloudWatch logs for any issues"
else
    echo ""
    echo "========================================="
    echo "✗ Deployment failed!"
    echo "========================================="
    exit 1
fi
