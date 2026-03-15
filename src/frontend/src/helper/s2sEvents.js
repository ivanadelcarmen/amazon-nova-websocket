import { DEFAULT_AUDIO_INPUT_CONFIG, DEFAULT_AUDIO_OUTPUT_CONFIG, DEFAULT_INFER_CONFIG, DEFAULT_SYSTEM_PROMPT, DEFAULT_TOOL_CONFIG } from '../agent/config.json'

// Stringify inputSchema JSON definitions for tools
DEFAULT_TOOL_CONFIG.tools.forEach(tool => {
  const schema = tool.toolSpec.inputSchema.json;
  tool.toolSpec.inputSchema.json = JSON.stringify(schema);
});

class S2sEvent {
  static DEFAULT_INFER_CONFIG = DEFAULT_INFER_CONFIG;
  static DEFAULT_SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT;
  static DEFAULT_AUDIO_INPUT_CONFIG = DEFAULT_AUDIO_INPUT_CONFIG;
  static DEFAULT_AUDIO_OUTPUT_CONFIG = DEFAULT_AUDIO_OUTPUT_CONFIG;
  static DEFAULT_TOOL_CONFIG = DEFAULT_TOOL_CONFIG;

  static sessionStart(inferenceConfig = S2sEvent.DEFAULT_INFER_CONFIG, turnSensitivity = "LOW") {
    return {
      event: {
        sessionStart: {
          inferenceConfiguration: inferenceConfig
        },
        // turnDetectionConfiguration: {
        //   endpointingSensitivity: turnSensitivity
        // }
      }
    };
  }

  static promptStart(promptName, audioOutputConfig = S2sEvent.DEFAULT_AUDIO_OUTPUT_CONFIG, toolConfig = S2sEvent.DEFAULT_TOOL_CONFIG) {
    return {
      "event": {
        "promptStart": {
          "promptName": promptName,
          "textOutputConfiguration": {
            "mediaType": "text/plain"
          },
          "audioOutputConfiguration": audioOutputConfig,

          "toolUseOutputConfiguration": {
            "mediaType": "application/json"
          },
          "toolConfiguration": toolConfig
        }
      }
    }
  }

  static contentStartText(promptName, contentName, role = "SYSTEM", interactive = false) {
    return {
      "event": {
        "contentStart": {
          "promptName": promptName,
          "contentName": contentName,
          "type": "TEXT",
          "interactive": interactive,
          "role": role,
          "textInputConfiguration": {
            "mediaType": "text/plain"
          }
        }
      }
    }
  }

  static textInput(promptName, contentName, systemPrompt = S2sEvent.DEFAULT_SYSTEM_PROMPT) {
    var evt = {
      "event": {
        "textInput": {
          "promptName": promptName,
          "contentName": contentName,
          "content": systemPrompt
        }
      }
    }
    return evt;
  }

  static contentEnd(promptName, contentName) {
    return {
      "event": {
        "contentEnd": {
          "promptName": promptName,
          "contentName": contentName
        }
      }
    }
  }

  static contentStartAudio(promptName, contentName, audioInputConfig = S2sEvent.DEFAULT_AUDIO_INPUT_CONFIG) {
      return {
        "event": {
          "contentStart": {
            "promptName": promptName,
            "contentName": contentName,
            "type": "AUDIO",
            "interactive": true,
            "audioInputConfiguration": audioInputConfig
          }
        }
      }
    }

  static audioInput(promptName, contentName, content) {
    return {
      event: {
        audioInput: {
          promptName,
          contentName,
          content,
        }
      }
    };
  }

  static contentStartTool(promptName, contentName, toolUseId) {
      return {
        event: {
          contentStart: {
            promptName,
            contentName,
            interactive: false,
            type: "TOOL",
            role: "TOOL",
            toolResultInputConfiguration: {
              toolUseId,
              type: "TEXT",
              textInputConfiguration: { mediaType: "text/plain" }
            }
          }
        }
      };
    }

  static textInputTool(promptName, contentName, content) {
      return {
        event: {
          toolResult: {
            promptName,
            contentName,
            content,
          }
        }
      };
    }

  static promptEnd(promptName) {
    return {
      event: {
        promptEnd: {
          promptName
        }
      }
    };
  }

  static sessionEnd() {
    return { event: { sessionEnd: {} } };
  }
}
export default S2sEvent;