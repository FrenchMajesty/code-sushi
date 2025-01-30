from typing import Dict, List, Optional
from .foundation_model_layer import FoundationModelLayer, ModelSize
from .together_model import TogetherModel
# Import other model implementations as needed

class ModelClient:
    """High-level client for interacting with foundation models."""
    
    SUPPORTED_PROVIDERS = {
        "together": TogetherModel,
        # "anthropic": AnthropicModel,
        # "openai": OpenAIModel,
        # etc.
    }
    
    def __init__(self, config: dict):
        """
        Initialize the model client with configuration.
        
        config format:
        {
            "provider": "together",
            "api_key": "your-api-key",
            "default_model_size": "large"  # optional, defaults to LARGE
        }
        """
        provider = config.get("provider", "together").lower()
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}. Available providers: {list(self.SUPPORTED_PROVIDERS.keys())}")
        
        self.model: FoundationModelLayer = self.SUPPORTED_PROVIDERS[provider](config["api_key"])
        self.default_size = ModelSize[config.get("default_model_size", "LARGE").upper()]
    
    def complete(self, messages: List[dict], model_size: Optional[ModelSize] = None) -> str:
        """
        Get a completion from the model.
        
        Args:
            messages: List of message dictionaries in the chat format
            model_size: Optional size override, otherwise uses default_size
        """
        size = model_size or self.default_size
        return self.model.send_completion_request(messages, size)
