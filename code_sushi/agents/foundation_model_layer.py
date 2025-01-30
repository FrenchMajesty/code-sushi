from abc import ABC, abstractmethod
from typing import Optional, List
from enum import Enum
from code_sushi.context import Context

class ModelSize(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

class FoundationModelLayer(ABC):
    """Abstract base class for the large language model APIs."""
    
    @abstractmethod
    def send_completion_request(self, history: List[dict], model_size: ModelSize) -> str:
        """
        Send a completion request to the language model API.
        """
        pass
