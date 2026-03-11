import aws_cdk as cdk
from cdk.stack import NovaVoiceAssistantDeployment

app = cdk.App()
NovaVoiceAssistantDeployment(app, "NovaVoiceAssistantStack")

app.synth()
