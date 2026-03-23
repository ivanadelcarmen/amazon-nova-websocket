#!/bin/bash

source ./lib/helpers.sh
source ./lib/aws.sh

# =======================
# Runtime
# =======================

parse_aws_args "$@"
setup_aws

# Verify ECR and ECS resources
ECR_REPO_NAME="novas2s-ecr-websocket"
ECS_CLUSTER="novas2s-ecs-cluster"
ECS_SERVICE="novas2s-ecs-service"

if aws ecr describe-repositories $AWS_ARGS --repository-names "$ECR_REPO_NAME" >/dev/null 2>&1; then
    ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"
    success "ECR URI: $ECR_URI"
else
    error "Repository $ECR_REPO_NAME does not exist"
fi

if ! aws ecs describe-clusters $AWS_ARGS --clusters "$ECS_CLUSTER" \
    --query "clusters[0].status" --output text 2>/dev/null | grep -q "ACTIVE"; then
    error "ECS cluster $ECS_CLUSTER does not exist"
fi

if ! aws ecs describe-services $AWS_ARGS --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" \
    --query "services[0].status" --output text 2>/dev/null | grep -q "ACTIVE"; then
    error "ECS service $ECS_SERVICE does not exist in cluster $ECS_CLUSTER"
fi

# Build and push the Docker image
log "Logging in to ECR..."
aws ecr get-login-password $AWS_ARGS --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

log "Building Docker image from root context..."
ROOT_DIR=".."
docker build -f "$ROOT_DIR/src/backend/websocket/Dockerfile" -t ${ECR_REPO_NAME}:latest $ROOT_DIR

log "Tagging Docker image..."
docker tag ${ECR_REPO_NAME}:latest ${ECR_URI}:latest

log "Pushing Docker image to ECR..."
docker push ${ECR_URI}:latest

success "Docker image successfully pushed to: ${ECR_URI}:latest"

# Update ECS service
log "Updating ECS service with one task..."
aws ecs update-service $AWS_ARGS \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE} \
    --force-new-deployment \
    --deployment-configuration "deploymentCircuitBreaker={enable=true,rollback=true}" \
    --desired-count 1 \
    --region ${AWS_REGION} \
    >/dev/null

success "ECS service update initiated successfully"

# Wait for ECS service to become stable
log "Waiting for ECS service to stabilize..."

if aws ecs wait services-stable $AWS_ARGS \
    --cluster "${ECS_CLUSTER}" \
    --services "${ECS_SERVICE}" \
    --region "${AWS_REGION}"; then

    success "ECS service deployment completed successfully"
else
    error "ECS service deployment failed or timed out"
fi

# Get the public IP of the task
log "Getting WebSocket server endpoint..."
TASK_ARN=$(aws ecs list-tasks $AWS_ARGS --cluster ${ECS_CLUSTER} --service-name ${ECS_SERVICE} --region ${AWS_REGION} --query 'taskArns[0]' --output text)

if [[ "$TASK_ARN" != "None" && -n "$TASK_ARN" ]]; then
    ENI_ID=$(aws ecs describe-tasks $AWS_ARGS --cluster ${ECS_CLUSTER} --tasks ${TASK_ARN} --region ${AWS_REGION} --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)
    
    PUBLIC_IP=$(aws ec2 describe-network-interfaces $AWS_ARGS --network-interface-ids ${ENI_ID} --region ${AWS_REGION} --query 'NetworkInterfaces[0].Association.PublicIp' --output text)
    
    echo "========================================"
    success "WebSocket URL: ws://${PUBLIC_IP}:8081"
    success "Health Check: http://${PUBLIC_IP}:8082/health"
    echo "========================================"
else
    warn "The ECS task is starting, has stopped, or timed out. Check the service or task logs for details"
fi