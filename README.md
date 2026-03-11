# Amazon Nova model cookbook 

## Getting Started

To get started with the code examples, ensure you have access to [Amazon Bedrock](https://aws.amazon.com/bedrock/). Then clone this repo and navigate to one of the folders above.

### Introduction

This project is for the [Amazon Nova Sonic speech-to-speech (S2S) workshop](https://catalog.workshops.aws/amazon-nova-sonic-s2s/en-US) and is intended for training purposes. It showcases a sample architecture for building applications that integrate with Nova Sonic, with features specifically designed to expose technical details for educational use.

The project includes two core components:
- A Python-based WebSocket server that manages the bidirectional streaming connection with Nova Sonic.
- A React front-end application that communicates with the S2S system through the WebSocket server.

### Enable AWS IAM permissions for Bedrock

To grant Bedrock access to your identity, you can:

- Open the [AWS IAM Console](https://us-east-1.console.aws.amazon.com/iam/home?#)
- Find your [Role](https://us-east-1.console.aws.amazon.com/iamv2/home?#/roles) (if using SageMaker or otherwise assuming an IAM Role), or else [User](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users)
- Select *Add Permissions > Create Inline Policy* to attach new inline permissions, open the *JSON* editor and paste in the below example policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockFullAccess",
            "Effect": "Allow",
            "Action": ["bedrock:*"],
            "Resource": "*"
        }
    ]
}
```

For more information on the fine-grained action and resource permissions in Bedrock, check out the [Bedrock Developer Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api.html).

### Prerequisites
- Python 3.12+
- Node.js 14+ and npm/yarn for UI development
- AWS account with Bedrock access
- AWS credentials configured locally
- In your AWS account, you can self-serve to gain access to the required model. Please refer to [this process](https://catalog.workshops.aws/amazon-nova-sonic-s2s/en-US/100-introduction/03-model-access) for guidance.
    - Titan text embedding v2
    - Nova Lite
    - Nova Micro
    - Nova Pro
    - Nova Sonic

## Installation instruction
Follow these instructions to build and launch both the Python WebSocket server and the React UI, which will allow you to converse with S2S and try out the basic features.

Clone the repository:
    
```bash
git clone https://github.com/aws-samples/amazon-nova-samples
mv amazon-nova-samples/speech-to-speech/workshops nova-s2s-workshop
rm -rf amazon-nova-samples
cd nova-s2s-workshop
```

### Install and start the Python websocket server
1. Start Python virtual machine
    ```
    cd python-server
    python3 -m venv .venv
    ```
    Mac
    ```
    source .venv/bin/activate
    ```
    Windows
    ```
    .venv\Scripts\activate
    ```

2. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set environment variables:
    
    The AWS access key and secret are required for the Python application, as they are needed by the underlying Smithy authentication library.
    ```bash
    export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET"
    export AWS_DEFAULT_REGION="us-east-1"
    ```
    The WebSocket host and port are optional. If not specified, the application will default to `localhost` and port `8081`.
    ```bash
    export HOST="localhost"
    export WS_PORT=8081
    ```
    The health check port is optional for container deployment such as ECS/EKS. If the environment variable below is not specified, the service will not start the HTTP endpoint for health checks.
    ```bash
    export HEALTH_PORT=8082 
    ```
    
4. Start the python websocket server
    ```bash
    python server.py
    ```

> Keep the Python WebSocket server running, then run the section below to launch the React web application, which will connect to the WebSocket service.

### Install and start the REACT frontend application
1. Navigate to the `react-client` folder
    ```bash
    cd react-client
    ```
2. Install
    ```bash
    npm install
    ```

3. This step is optional: set environment variables for the React app. If not provided, the application defaults to `ws://localhost:8081`.

    ```bash
    export REACT_APP_WEBSOCKET_URL='YOUR_WEB_SOCKET_URL'
    ```

4. If you want to run the React code outside the workshop environment, update the `homepage` value in the `react-client/package.json` file from "/proxy/3000/" to "."

5. Run
    ```
    npm start
    ```

When using Chrome, if there’s no sound, please ensure the sound setting is set to Allow

⚠️ **Warning:** Known issue: This UI is intended for demonstration purposes and may encounter state management issues after frequent conversation start/stop actions. Refreshing the page can help resolve the issue.

### Strands Agent integration
This application demonstrates how to use a [Strands Agent](https://community.aws/content/2xCUnoqntk2PnWDwyb9JJvMjxKA/step-by-step-guide-setting-up-a-strands-agent-with-aws-bedrock) to orchestrate external workflows, integrating [AWS Location MCP server](https://github.com/awslabs/mcp?tab=readme-ov-file#aws-location-service-mcp-server) and a sample Weather tool, showcasing advanced agent reasoning and orchestration.

## Contributing

We welcome community contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
