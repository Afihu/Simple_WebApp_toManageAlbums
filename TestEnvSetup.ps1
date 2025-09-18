# PowerShell script to set up LocalStack and apply Terraform
# Start LocalStack using Docker Compose
Write-Host "Starting LocalStack via Docker Compose..."
docker-compose up -d

# Wait for LocalStack to be ready
Write-Host "Waiting for LocalStack to be ready..."
$maxAttempts = 20
$attempt = 0
$ready = $false
while (-not $ready -and $attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri http://localhost:4566/health -UseBasicParsing -TimeoutSec 3
        if ($response.Content -match '"initScripts":\s*\{"initialized":true\}') {
            $ready = $true
        } else {
            Start-Sleep -Seconds 3
        }
    } catch {
        Start-Sleep -Seconds 3
    }
    $attempt++
}
if (-not $ready) {
    Write-Error "LocalStack did not become ready in time."
    exit 1
}
Write-Host "LocalStack is ready."

# Initialize and apply Terraform for test-localstack.tf and test-localstack-apigw.tf
$terraformDirs = @(".")
foreach ($tfFile in @("test-localstack.tf", "test-localstack-apigw.tf")) {
    Write-Host "Applying Terraform file: $tfFile"
    terraform init -input=false
    terraform apply -auto-approve -input=false -var-file=$tfFile
}
Write-Host "Environment setup complete."
