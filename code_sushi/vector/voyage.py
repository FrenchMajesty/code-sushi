import voyageai
from typing import List
from code_sushi.context import Context, LogLevel
import time

class Voyage:
    """
    Wrapper class for Voyager.ai which is used for embedding and reranking
    """
    _instance = None

    def __init__(self, context: Context):
        api_key = context.voyage_ai_config.get("api_key")
        self.vo = voyageai.Client(api_key=api_key)
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
            embedding_model = self.context.voyage_ai_config.get("embedding_model")
            result = self.vo.embed(
                texts=texts, 
                model=embedding_model, 
                input_type=input_type,
            )
            
            return result.embeddings
        except Exception as e:
            print(f"Error embedding texts: {e}")
            return []
    
    def rerank(self, query: str, texts: List[str], top_k = 5) -> List[str]:
        """
        Re-rank the search results to pick the most relevant context snippets for the query.
        """
        try:
            if not texts:
                return []

            start = time.time()

            if self.context.is_log_level(LogLevel.VERBOSE):
                print("Starting to rerank docs...")

            rerank_model = self.context.voyage_ai_config.get("rerank_model")
            res = self.vo.rerank(query, texts, rerank_model, top_k=top_k)
            outcome = [result.document for result in res.results]

            if self.context.is_log_level(LogLevel.VERBOSE):
                runtime = time.time() - start
                print(f"Reranker ran in {runtime:.2f} seconds")
            return outcome
        except Exception as e:
            print(f"Error in Voyage.rerank(): {e}")
            raise
