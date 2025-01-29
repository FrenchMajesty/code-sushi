import voyageai
from dotenv import load_dotenv
from typing import List
from code_sushi.context import Context

load_dotenv()

class VoyageEmbed:
    _instance = None

    def __init__(self, context: Context):
        self.vo = voyageai.Client()
        self.context = context

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
            if not texts:
                return []

            res = self.vo.rerank(query, texts, "rerank-2-lite", top_k=5)
            outcome = [result.document for result in res.results]

            return outcome
        except Exception as e:
            print(f"Error reranking texts: {e}")
            raise
