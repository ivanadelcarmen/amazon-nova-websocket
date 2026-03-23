#!/bin/bash

source ./lib/helpers.sh
source ./lib/aws.sh

# =======================
# Runtime
# =======================

parse_aws_args "$@"
setup_aws

# Destroy stack
log "Destroying CDK stack..."

cd ../src/backend
cdk destroy --force $AWS_ARGS

success "CDK stack destroyed successfully"
