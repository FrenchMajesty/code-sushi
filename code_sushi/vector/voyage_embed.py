import voyageai
from dotenv import load_dotenv
from typing import List

load_dotenv()

class VoyageEmbed:
    _instance = None

    def __init__(self):
        self.vo = voyageai.Client()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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
    
    def rerank(self, query: str, texts: List[str]) -> List[str]:
        """
        Re-rank the search results to pick the most relevant context snippets for the query.
        """
        try:
            res = self.vo.rerank(query, texts, "rerank-2-lite", top_k=5)
            outcome = [text for text in res["reranked_texts"]]
            return outcome
        except Exception as e:
            print(f"Error reranking texts: {e}")
            raise
