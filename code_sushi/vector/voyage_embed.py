import voyageai
from dotenv import load_dotenv
from typing import List

load_dotenv()

class VoyageEmbed:
    _instance = None

    def __init__(self):
        self.vo = voyageai.Client()

    def __new__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super().__new__(self, *args, **kwargs)
        return self._instance

    def embed(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """
        Embeds text using Voyage AI.
        """
        try:
            result = self.vo.embed(
                texts=texts, 
                model="voyage-code-3", 
                input_type=input_type,
            )

            return result.embeddings
        except Exception as e:
            print(f"Error embedding texts: {e}")
            return []
