import asyncio
import json
import warnings
import uuid
import time
import traceback

from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
from aws_sdk_bedrock_runtime.config import Config
from smithy_aws_core.identity import EnvironmentCredentialsResolver
from smithy_core.aio.identity import ChainedIdentityResolver
from smithy_http.aio.crt import AWSCRTHTTPClient

from s2s_events import S2sEvent

# Suppress warnings
warnings.filterwarnings("ignore")

DEBUG = False


def debug_print(message):
    """Print only if debug mode is enabled"""
    if DEBUG:
        print(message)


class S2sSessionManager:
    """Manages bidirectional streaming with AWS Bedrock using asyncio"""
    
    def __init__(self, region, model_id='amazon.nova-sonic-v1:0', strands_agent=None):
        """Initialize the stream manager."""
        self.model_id = model_id
        self.region = region
        
        # Audio and output queues
        self.audio_input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        
        self.response_task = None
        self.stream = None
        self.is_active = False
        self.bedrock_client = None
        
        # Session information
        self.prompt_name = None  # Will be set from frontend
        self.content_name = None  # Will be set from frontend
        self.audio_content_name = None  # Will be set from frontend
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = ""
        self.strands_agent = strands_agent

    def _initialize_client(self):
        """Initialize the Bedrock client with SigV4 authentication"""
        # Create credential chain through environment variables
        credential_resolver = ChainedIdentityResolver(
            resolvers=(
                EnvironmentCredentialsResolver()
            )
        )
        
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=credential_resolver,
        )
        self.bedrock_client = BedrockRuntimeClient(config=config)

    def reset_session_state(self):
        """Reset session state for a new session."""
        # Clear queues
        while not self.audio_input_queue.empty():
            try:
                self.audio_input_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Reset tool use state
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = ""
        
        # Reset session information
        self.prompt_name = None
        self.content_name = None
        self.audio_content_name = None

    async def initialize_stream(self):
        """Initialize the bidirectional stream with Bedrock."""
        try:
            if not self.bedrock_client:
                self._initialize_client()

        except Exception as e:
            self.is_active = False
            print(f"Failed to initialize Bedrock client: {str(e)}")
            traceback.print_exc()
            raise

        try:
            # Initialize the stream with a 10 second timeout
            self.stream = await asyncio.wait_for(
                self.bedrock_client.invoke_model_with_bidirectional_stream(
                    InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)
                ),
                timeout=10
            )
            self.is_active = True
            
            # Start listening for responses
            self.response_task = asyncio.create_task(self._process_responses())

            # Start processing audio input
            asyncio.create_task(self._process_audio_input())
            
            # Wait a bit to ensure everything is set up
            await asyncio.sleep(0.1)
            
            return self
        
        except asyncio.TimeoutError:
            self.is_active = False
            print(f"TIMEOUT: Bedrock API did not respond within 10 seconds")
            print(f"Model: {self.model_id}")
            print(f"Region: {self.region}")
            traceback.print_exc()
            raise

        except Exception as e:
            self.is_active = False
            print(f"Failed to initialize stream: {str(e)}")
            traceback.print_exc()
            raise
    
    async def send_raw_event(self, event_data):
        try:
            """Send a raw event to the Bedrock stream."""
            if not self.stream or not self.is_active:
                debug_print("Stream not initialized or closed")
                return
            
            event_json = json.dumps(event_data)
            #if "audioInput" not in event_data["event"]:
            #    print(event_json)
            event = InvokeModelWithBidirectionalStreamInputChunk(
                value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
            )
            await self.stream.input_stream.send(event)

            # Close session
            if "sessionEnd" in event_data["event"]:
                self.close()
            
        except Exception as e:
            debug_print(f"Error sending event: {str(e)}")
    
    async def _process_audio_input(self):
        """Process audio input from the queue and send to Bedrock."""
        while self.is_active:
            try:
                # Get audio data from the queue
                data = await self.audio_input_queue.get()
                
                # Extract data from the queue item
                prompt_name = data.get('prompt_name')
                content_name = data.get('content_name')
                audio_bytes = data.get('audio_bytes')
                
                if not audio_bytes or not prompt_name or not content_name:
                    debug_print("Missing required audio data properties")
                    continue

                # Create the audio input event
                audio_event = S2sEvent.audio_input(prompt_name, content_name, audio_bytes.decode('utf-8') if isinstance(audio_bytes, bytes) else audio_bytes)
                
                # Send the event
                await self.send_raw_event(audio_event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                debug_print(f"Error processing audio: {e}")
                if DEBUG:
                    import traceback
                    traceback.print_exc()
    
    def add_audio_chunk(self, prompt_name, content_name, audio_data):
        """Add an audio chunk to the queue."""
        # The audio_data is already a base64 string from the frontend
        self.audio_input_queue.put_nowait({
            'prompt_name': prompt_name,
            'content_name': content_name,
            'audio_bytes': audio_data
        })
    
    async def _process_responses(self):
        """Process incoming responses from Bedrock."""
        while self.is_active:
            try:            
                output = await self.stream.await_output()
                result = await output[1].receive()
                
                if result.value and result.value.bytes_:
                    response_data = result.value.bytes_.decode('utf-8')
                    
                    json_data = json.loads(response_data)
                    json_data["timestamp"] = int(time.time() * 1000)  # Milliseconds since epoch
                    
                    event_name = None
                    if 'event' in json_data:
                        event_name = list(json_data["event"].keys())[0]
                        # if event_name == "audioOutput":
                        #     print(json_data)
                        
                        # Handle tool use detection
                        if event_name == 'toolUse':
                            self.toolUseContent = json_data['event']['toolUse']
                            self.toolName = json_data['event']['toolUse']['toolName']
                            self.toolUseId = json_data['event']['toolUse']['toolUseId']
                            debug_print(f"Tool use detected: {self.toolName}, ID: {self.toolUseId}, "+ json.dumps(json_data['event']))

                        # Process tool use when content ends
                        elif event_name == 'contentEnd' and json_data['event'][event_name].get('type') == 'TOOL':
                            prompt_name = json_data['event']['contentEnd'].get("promptName")
                            debug_print("Processing tool use and sending result")
                            toolResult = await self.processToolUse(self.toolName, self.toolUseContent)
                                
                            # Send tool start event
                            toolContent = str(uuid.uuid4())
                            tool_start_event = S2sEvent.content_start_tool(prompt_name, toolContent, self.toolUseId)
                            await self.send_raw_event(tool_start_event)
                            
                            # Also send tool start event to WebSocket client
                            tool_start_event_copy = tool_start_event.copy()
                            tool_start_event_copy["timestamp"] = int(time.time() * 1000)
                            await self.output_queue.put(tool_start_event_copy)
                            
                            # Send tool result event
                            if isinstance(toolResult, dict):
                                content_json_string = json.dumps(toolResult)
                            else:
                                content_json_string = toolResult

                            tool_result_event = S2sEvent.text_input_tool(prompt_name, toolContent, content_json_string)
                            print("Tool result", tool_result_event)
                            await self.send_raw_event(tool_result_event)
                            
                            # Also send tool result event to WebSocket client
                            tool_result_event_copy = tool_result_event.copy()
                            tool_result_event_copy["timestamp"] = int(time.time() * 1000)
                            await self.output_queue.put(tool_result_event_copy)

                            # Send tool content end event
                            tool_content_end_event = S2sEvent.content_end(prompt_name, toolContent)
                            await self.send_raw_event(tool_content_end_event)
                            
                            # Also send tool content end event to WebSocket client
                            tool_content_end_event_copy = tool_content_end_event.copy()
                            tool_content_end_event_copy["timestamp"] = int(time.time() * 1000)
                            await self.output_queue.put(tool_content_end_event_copy)
                    
                    # Put the response in the output queue for forwarding to the frontend
                    await self.output_queue.put(json_data)

            except json.JSONDecodeError as ex:
                print(f"JSON decode error: {ex}")
                await self.output_queue.put({"raw_data": response_data})

            except StopAsyncIteration:
                # Stream has ended normally
                print("Stream ended")
                break

            except Exception as e:
                # Handle ValidationException properly
                if "ValidationException" in str(e):
                    error_message = str(e)
                    print(f"Validation error: {error_message}")

                    # Don't break on validation errors, just log them
                    await self.output_queue.put({"error": "validation_error", "message": error_message})

                elif "InvalidStateError" in str(e) or "CANCELLED" in str(e):
                    # HTTP client cancellation - log but don't break
                    print(f"HTTP client state error (can be ignored): {e}")
                    
                else:
                    print(f"Error receiving response: {e}")
                    import traceback
                    traceback.print_exc()
                    # Only break on serious errors
                    break

        self.is_active = False
        self.close()

    async def processToolUse(self, toolName, toolUseContent):
        """Return the tool result"""
        print(f"Tool Use Content: {toolUseContent}")

        toolName = toolName.lower()
        content, result = None, None
        try:
            if toolUseContent.get("content"):
                # Parse the JSON string in the content field
                query_json = json.loads(toolUseContent.get("content"))
                content = toolUseContent.get("content")  # Pass the JSON string directly to the agent
                print(f"Extracted query: {content}")

            # Simple toolUse to get system time in UTC
            if toolName == "getdatetool":
                from datetime import datetime, timezone
                result = datetime.now(timezone.utc).strftime('%A, %Y-%m-%d %H-%M-%S')

            if not result:
                result = "no result found"

            return {"result": result}
            
        except Exception as ex:
            print(f"Exception in processToolUse: {ex}")
            traceback.print_exc()
            return {"result": "An error occurred while attempting to retrieve information related to the toolUse event."}
    
    async def close(self):
        """Close the stream properly."""
        if not self.is_active:
            return
            
        self.is_active = False
        
        # Clear audio queue to prevent processing old audio data
        while not self.audio_input_queue.empty():
            try:
                self.audio_input_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Clear output queue
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Reset tool use state
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = ""
        
        # Reset session information
        self.prompt_name = None
        self.content_name = None
        self.audio_content_name = None
        
        if self.stream:
            try:
                await self.stream.input_stream.close()
            except Exception as e:
                debug_print(f"Error closing stream: {e}")
        
        if self.response_task and not self.response_task.done():
            self.response_task.cancel()
            try:
                await self.response_task
            except asyncio.CancelledError:
                pass
        
        # Set stream to None to ensure it's properly cleaned up
        self.stream = None
        self.response_task = None
        