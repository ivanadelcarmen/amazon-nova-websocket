from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_logs as logs,
    RemovalPolicy,
    Duration
)
from constructs import Construct

class NovaVoiceAssistantDeployment(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECR repository for the WebSocket server
        ecr_repo = ecr.Repository(
            self, "WebSocketServerRepository",
            repository_name="novas2s-ecr-websocket",
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True
        )

        # Create VPC with only public subnets
        vpc = ec2.Vpc(
            self, "NovaS2SVPC",
            vpc_name="novas2s-vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # Create security group for ECS tasks
        security_group = ec2.SecurityGroup(
            self, "WebSocketSecurityGroup",
            vpc=vpc,
            description="Security group for Nova S2S WebSocket server",
            allow_all_outbound=True
        )

        # Allow WebSocket traffic (port 8081)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8081),
            description="Allow WebSocket connections"
        )

        # Allow health check traffic (port 8082)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8082),
            description="Allow health check connections"
        )

        # Create ECS cluster
        cluster = ecs.Cluster(
            self, "NovaS2SCluster",
            vpc=vpc,
            cluster_name="novas2s-ecs-cluster"
        )

        # Create task execution role
        task_execution_role = iam.Role(
            self, "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ]
        )

        # Create task role with Bedrock permissions
        task_role = iam.Role(
            self, "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate",
                    "bedrock:Converse",
                    "bedrock:ConverseStream"
                ],
                resources=["*"]
            )
        )

        # Add Bedrock Agent Core permissions
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock-agentcore:*"
                ],
                resources=["*"]
            )
        )

        # Add Location Services permissions for MCP
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "geo:SearchPlaceIndexForText",
                    "geo:SearchPlaceIndexForPosition",
                    "geo:GetPlace"
                ],
                resources=["*"]
            )
        )

        # Add DynamoDB permissions for Bedrock Agents
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=["*"]
            )
        )

        # Add Lambda permissions for Bedrock Agents
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "lambda:InvokeFunction"
                ],
                resources=["*"]
            )
        )

        # Create CloudWatch log group
        log_group = logs.LogGroup(
            self, "WebSocketLogGroup",
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Fargate task definition
        task_definition = ecs.FargateTaskDefinition(
            self, "WebSocketTaskDef",
            memory_limit_mib=2048,
            cpu=1024,
            execution_role=task_execution_role,
            task_role=task_role
        )

        # Add container to task definition
        container = task_definition.add_container(
            "WebSocketContainer",
            image=ecs.ContainerImage.from_ecr_repository(ecr_repo, "latest"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="websocket",
                log_group=log_group
            ),
            environment={
                "HOST": "0.0.0.0",
                "WS_PORT": "8081",
                "HEALTH_PORT": "8082",
                "AWS_DEFAULT_REGION": self.region
            },
            port_mappings=[
                ecs.PortMapping(
                    container_port=8081,
                    protocol=ecs.Protocol.TCP
                ),
                ecs.PortMapping(
                    container_port=8082,
                    protocol=ecs.Protocol.TCP
                )
            ],
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:8082/health || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60)
            )
        )

        # Create Fargate service
        service = ecs.FargateService(
            self, "WebSocketService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=0,  # Start with 0, scale up after image push
            assign_public_ip=True,
            security_groups=[security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            service_name="novas2s-ecs-service"
        )

        # Output the ECR repository URI
        CfnOutput(
            self, "ECRRepositoryURI",
            value=ecr_repo.repository_uri,
            description="ECR Repository URI for WebSocket server"
        )

        # Output the VPC ID
        CfnOutput(
            self, "VPCID",
            value=vpc.vpc_id,
            description="VPC ID"
        )

        # Output the security group ID
        CfnOutput(
            self, "SecurityGroupID",
            value=security_group.security_group_id,
            description="Security Group ID"
        )

        # Output the ECS cluster name
        CfnOutput(
            self, "ClusterName",
            value=cluster.cluster_name,
            description="ECS Cluster Name"
        )

        # Output the service name
        CfnOutput(
            self, "ServiceName",
            value=service.service_name,
            description="ECS Service Name"
        )

        # Store ECR repo for reference
        self.ecr_repository = ecr_repo
