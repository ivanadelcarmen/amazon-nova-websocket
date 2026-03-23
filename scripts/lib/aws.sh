#!/bin/bash

source ./lib/helpers.sh

# =======================
# Runtime
# =======================

parse_aws_args() {
    while getopts "p:" opt; do
        case "$opt" in
            p) AWS_PROFILE="$OPTARG";;
            \?) error "Invalid argument: -$OPTARG";;
        esac
    done
}

setup_aws() {
    log "Fetching AWS profile configuration..."
    
    # Set AWS profile
    AWS_ARGS=""
    if [[ -n "$AWS_PROFILE" ]]; then
        AWS_ARGS="--profile $AWS_PROFILE"
        success "AWS Profile: $AWS_PROFILE"
    else
        success "AWS Profile: DEFAULT"
    fi

    # Get AWS account ID and region
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity $AWS_ARGS --query Account --output text)
    AWS_REGION=${AWS_DEFAULT_REGION:-"us-east-1"}

    if [ -z "$AWS_ACCOUNT_ID" ]; then
        error "Could not determine AWS account ID"
    fi

    success "AWS Account ID: ${AWS_ACCOUNT_ID}"
    success "AWS Region: ${AWS_REGION}"
}