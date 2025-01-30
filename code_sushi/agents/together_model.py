from together import Together
from typing import List
from .foundation_model_layer import FoundationModelLayer, ModelSize

class TogetherModel(FoundationModelLayer):
    """Implementation of FoundationModelLayer using Together AI's API"""
    
    def __init__(self, config: dict):
        self.client = Together(api_key=config["api_key"])
        self.primary_model = config["primary_chat_model"]
        self.secondary_model = config["secondary_chat_model"]
        self.models = {
            ModelSize.SMALL: self.secondary_model,
            ModelSize.MEDIUM: self.primary_model,
            ModelSize.LARGE: self.primary_model
        }
    
    def send_completion_request(self, history: List[dict], model_size: ModelSize) -> str:
        """
        Send a completion request to Together AI's API.
        """
        model = self.models[model_size]
        
        completion = self.client.chat.completions.create(
            model=model,
            messages=history
        )
        
        return completion.choices[0].message.content
