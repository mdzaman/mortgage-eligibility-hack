# AWS CDK Deployment for Mortgage Eligibility Engine

## Architecture

- **AWS Lambda**: Runs the mortgage engine logic
- **API Gateway**: REST API endpoints
- **Serverless**: No infrastructure management required

## Endpoints

- `GET /` - Web interface
- `POST /evaluate` - Mortgage evaluation API
- `GET /presets` - Sample scenarios

## Deployment

```bash
# Install AWS CDK CLI
npm install -g aws-cdk

# Deploy the stack
./deploy.sh
```

## Manual Steps

```bash
cd cdk
pip install -r requirements.txt
cdk bootstrap  # First time only
cdk deploy
```

The API Gateway URL will be output after deployment.
