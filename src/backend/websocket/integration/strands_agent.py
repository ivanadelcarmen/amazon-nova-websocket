import os
import json
import re

import boto3 
from strands import Agent
from strands.models import BedrockModel
from strands_tools import tavily
from strands_tools import retrieve


class StrandsAgent:
    """
    The Strands Agent definition to be passed to the S2S session manager when
    running the WebSocket server, which runs on Amazon Nova Lite and includes two
    coded tools for Tavily web search and Bedrock Knowledge Base retrieval.

    For both tools to work, the following environment variables must be set
    before running the server:

        1. KNOWLEDGE_BASE_ID
        2. TAVILY_API_KEY
    """
    def __init__(self):
        session = boto3.Session(
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )

        # Specify Bedrock LLM for the Agent
        bedrock_model = BedrockModel(
            model_id="amazon.nova-lite-v1:0",
            boto_session=session
        )

        tools = [tavily, retrieve] # ADD TOOLS HERE

        self.agent = Agent(
            tools=tools, 
            model=bedrock_model,
            system_prompt=
            """
                You are a helpful assistant with access to two powerful tools:

                1. tavily - For web searches and current information
                Use this tool for:
                - Current events, news, or recent information
                - Facts that may have changed recently
                - Information about specific places, businesses, locations, or concepts
                - Any question that requires up-to-date or real-world data
                - Questions about things happening now or recently

                2. retrieve - For querying the knowledge base
                Use this tool for:
                - Domain-specific information stored in the knowledge base
                - Company documentation, policies, or internal data
                - Questions about information that should be in the knowledge base
                - Detailed information about specific topics covered in the knowledge base

                Keep your responses CONCISE and SHORT (2-3 sentences maximum). This is for a voice conversation, so brevity is essential.

                Always provide your final response within <response></response> tags.
            """
        )


    '''
    Send the input to the agent, allowing it to handle tool selection and invocation. 
    The response will be generated after the selected LLM performs reasoning. 
    This approach is suitable when you want to delegate tool selection logic to the agent, and have a generic toolUse definition in Sonic ToolUse.
    Note that the reasoning process may introduce latency, so it's recommended to use a lightweight model such as Nova Lite.
    Sample parameters: input="largest zoo in Seattle?"
    '''
    def query(self, input):
        output = str(self.agent(input))
        if "<response>" in output and "</response>" in output:
            match = re.search(r"<response>(.*?)</response>", output, re.DOTALL)
            if match:
                output = match.group(1)
        elif "<answer>" in output and "</answer>" in output:
            match = re.search(r"<answer>(.*?)</answer>", output, re.DOTALL)
            if match:
                output = match.group(1)
        return output

    '''
    Invoke the tool directly and return the raw response without any reasoning.
    This approach is suitable when tool selection is managed within Sonic and the exact toolName is already known. 
    It offers lower query latency, as no additional reasoning is performed by the agent.
    Sample parameters: tool_name="search_places", input="largest zoo in Seattle"
    '''
    def call_tool(self, tool_name, input):
        if isinstance(input, str):
            input = json.loads(input)
        if "query" in input:
            input = input.get("query")

        tool_func = getattr(self.agent.tool, tool_name)
        return tool_func(query=input)
