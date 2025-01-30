from together import Together
from typing import List
from .foundation_model_layer import FoundationModelLayer, ModelSize

class TogetherModel(FoundationModelLayer):
    """Implementation of FoundationModelLayer using Together AI's API"""
    
    def __init__(self, api_key: str):
        self.client = Together(api_key=api_key)
        self.models = {
            ModelSize.SMALL: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
            ModelSize.MEDIUM: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            ModelSize.LARGE: "meta-llama/Llama-3.3-70B-Instruct-Turbo"
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
