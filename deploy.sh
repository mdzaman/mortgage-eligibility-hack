#!/bin/bash
set -e

echo "Installing CDK dependencies..."
cd cdk
pip install -r requirements.txt

echo "Bootstrapping CDK (if needed)..."
cdk bootstrap

echo "Deploying stack..."
cdk deploy --require-approval never

echo "Deployment complete!"
