#!/bin/bash

source ./lib/helpers.sh

# =======================
# Runtime
# =======================

parse_aws_args() {
    while getopts "p:k:t:" opt; do
        case "$opt" in
            p) AWS_PROFILE="$OPTARG";;
            k) KNOWLEDGE_BASE_ID="$OPTARG";;
            t) TAVILY_API_KEY="$OPTARG";;
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

get_cdk_contexts() {
    log "Fetching CDK context parameters..."

    # Set CDK context arguments
    CDK_ARGS=""

    if [[ -n "$KNOWLEDGE_BASE_ID" ]]; then
        CDK_ARGS="-c bedrock_kb=${KNOWLEDGE_BASE_ID}"
        success "Bedrock Knowledge Base ID: $KNOWLEDGE_BASE_ID"
    else
        warn "Bedrock Knowledge Base ID: NOT SET"
    fi

    if [[ -n "$TAVILY_API_KEY" ]]; then
        CDK_ARGS="${CDK_ARGS} -c tavily_key=${TAVILY_API_KEY}"
        success "Tavily API Key: ${TAVILY_API_KEY:0:10}..."
    else
        warn "Tavily API Key: NOT SET"
    fi
}