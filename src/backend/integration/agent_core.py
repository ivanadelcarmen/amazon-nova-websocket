import boto3
import json
import os

bank_agent_arn = os.environ.get("AGENT_CORE_RUNTIME_ARN_BANKING_AGENT")
mortgage_agent_arn = os.environ.get("AGENT_CORE_RUNTIME_ARN_MORTGAGE_AGENT")
if not bank_agent_arn or not mortgage_agent_arn:
    # Get AgentCore Runtime ARNS
    agentcore_control = boto3.client('bedrock-agentcore-control')
    rt_response= agentcore_control.list_agent_runtimes()
    for rt in rt_response["agentRuntimes"]:
        if rt["agentRuntimeName"] == "sonic_workshop_banking_agent":
            bank_agent_arn = rt["agentRuntimeArn"]
            os.environ["AGENT_CORE_RUNTIME_ARN_BANKING_AGENT"] = bank_agent_arn
        elif rt["agentRuntimeName"] == "sonic_workshop_mortgage_agent":
            mortgage_agent_arn = rt["agentRuntimeArn"]
            os.environ["AGENT_CORE_RUNTIME_ARN_MORTGAGE_AGENT"] = mortgage_agent_arn

ARNS = {
    "ac_bank_agent": bank_agent_arn,
    "ac_mortgage_agent": mortgage_agent_arn
}
agentcore_client = boto3.client('bedrock-agentcore',region_name='us-east-1')


def invoke_agent_core(tool_name, payload):
    try:
        arn = ARNS.get(tool_name.lower())
        if not arn:
            return {"result": "AgentCore runtime doesn't exist"}
        if isinstance(payload, dict):
            payload = json.dumps({"account_id":"940y22688","query":"account balance"})

        boto3_response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=arn,
            qualifier="DEFAULT",
            payload=json.dumps(payload)
        )
        if "text/event-stream" in boto3_response.get("contentType", ""):
            content = []
            for line in boto3_response["response"].iter_lines(chunk_size=1):
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        line = line[6:]
                        print(line)
                        content.append(line)
            return "\n".join(content)
        else:
            try:
                events = []
                for event in boto3_response.get("response", []):
                    events.append(event)
            except Exception as e:
                events = [f"Error reading EventStream: {e}"]
            return json.loads(events[0].decode("utf-8"))
    except Exception as e:
        return {"result": f"Failed to call agent core runtime: {e}"}