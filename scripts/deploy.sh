#!/bin/bash

source ./lib/helpers.sh
source ./lib/aws.sh

# =======================
# Runtime
# =======================

parse_aws_args "$@"
setup_aws

get_cdk_contexts

# Deploy stack
log "Deploying CDK stack..."

cd ../src/backend
cdk bootstrap $AWS_ARGS
cdk deploy --require-approval never $CDK_ARGS $AWS_ARGS

success "CDK deployment successful"

# Build and push Docker image, update ECS service, and get URLs
log "Starting Docker build and push process..."

cd ../../scripts
if [[ -n "$AWS_PROFILE" ]]; then
    ./build.sh -p $AWS_PROFILE
else
    ./build.sh
fi
