from openai import OpenAI
from typing import List, AsyncIterator
from code_sushi.context import Context, LogLevel
from .foundation_model_layer import FoundationModelLayer, ModelSize

class OpenAIModel(FoundationModelLayer):
    """
    Implementation of FoundationModelLayer using OpenAI's API
    """
    def __init__(self, context: Context, config: dict):
        self.context = context
        self.client = OpenAI(api_key=config["api_key"])
        self.primary_model = config["primary_chat_model"]
        self.secondary_model = config["secondary_chat_model"]
        self.models = {
            ModelSize.SMALL: self.secondary_model,
            ModelSize.MEDIUM: self.primary_model,
            ModelSize.LARGE: self.primary_model
        }
    
    def send_completion_request(self, history: List[dict], model_size: ModelSize) -> str:
        """
        Send a completion request to OpenAI's API.
        """
        model = self.models[model_size]
        show_logs = self.context.is_log_level(LogLevel.DEBUG)
        start = self.track_start(show_logs)

        completion = self.client.chat.completions.create(
            model=model,
            messages=history
        )

        self.track_end(show_logs, start)
        return completion.choices[0].message.content

    async def stream_completion_request(self, history: List[dict], model_size: ModelSize) -> AsyncIterator[str]:
        """
        Send a streaming completion request to OpenAI's API.
        """
        model = self.models[model_size]
        show_logs = self.context.is_log_level(LogLevel.DEBUG)
        start = self.track_start(show_logs)

        completion = self.client.chat.completions.create(
            model=model,
            messages=history,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

        self.track_end(show_logs, start)
