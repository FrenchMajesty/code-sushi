from abc import ABC, abstractmethod
from typing import Optional, List
from enum import Enum
from code_sushi.context import Context
import time

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

    def track_start(self, can_proceed: bool) -> float:
        """
        Track the start of the request.
        """
        start = time.time()
        if can_proceed:
            print(f"Sending completion req to LLM")
        return start

    def track_end(self, can_proceed: bool, start: float) -> None:
        """
        Track the end of the request.
        """
        if can_proceed:
            runtime = time.time() - start
            print(f"Received response from LLM in {runtime:.2f} seconds")
