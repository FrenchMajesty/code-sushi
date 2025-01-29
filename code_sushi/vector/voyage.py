import voyageai
from dotenv import load_dotenv
from typing import List
from code_sushi.context import Context, LogLevel
import time

load_dotenv()

class Voyage:
    """
    Wrapper class for Voyager.ai which is used for embedding and reranking
    """
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

            start = time.time()

            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print("Starting to rerank docs...")

            res = self.vo.rerank(query, texts, "rerank-2-lite", top_k=5)
            outcome = [result.document for result in res.results]

            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                runtime = time.time() - start
                print(f"Reranker ran in {runtime:.2f} seconds")
            return outcome
        except Exception as e:
            print(f"Error in Voyage.rerank(): {e}")
            raise
