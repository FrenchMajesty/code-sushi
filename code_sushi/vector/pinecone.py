from pinecone import Pinecone as PineconeClient
from typing import Optional, List
from .vector_record import VectorRecord
from code_sushi.context import Context, LogLevel
from .utils import chunks
import time
import os

class Pinecone:
    """
    Responsible for interacting with the Pinecone API for managing indexes and vector DB entries.
    """
    def __init__(self, context: Context, index_name: Optional[str] = None, pool_threads: int = 30):
        self.context = context 

        api_key = os.getenv("SUSHI_PINECONE_API_KEY")
        self.client = PineconeClient(api_key=api_key, pool_threads=pool_threads)

        if not index_name:
            index_name = os.getenv("SUSHI_PINECONE_INDEX_NAME")
        
        self.index = self.client.Index(index_name, pool_threads=pool_threads)
    
    def write_many(self, records: List[VectorRecord], chunk_size: int = 400, namespace: str ="anonymous"):
        """
        Write many records at once to the Pinecone index.
        """
        items = []
        start = time.time()
        for record in records:
            items.append({
                "id": record.key,
                "values": record.embedding,
                "metadata": record.metadata
            })

        if self.context.log_level >= LogLevel.VERBOSE:
            print(f"Batch writing {len(items)} items to index, namespace {namespace}")

        with self.index as index:
            # Send chunked requests in parallel
            async_results = [
                index.upsert(vectors=ids_vectors_chunk, async_req=True, namespace=namespace)
                for ids_vectors_chunk in chunks(items, chunk_size)
            ]

            # Wait for and retrieve responses (this raises in case of error)
            res = [async_result.get() for async_result in async_results]
            
            if self.context >= LogLevel.VERBOSE:
                runtime = time.time() - start
                print(f"Batch write finished in {runtime:.2f} seconds")

            return len(res)


    
