from typing import List

class VectorRecord:
    """
    Represents a record already stored or to-be stored in our Vector DB.
    """
    def __init__(self, key: str, text: str, metadata: dict = {}):
        self.key: str = key
        self.text: str = text
        self.metadata: dict = metadata
        self.embedding: List[float] = []
