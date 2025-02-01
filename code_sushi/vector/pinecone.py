from pinecone import Pinecone as PineconeClient
from typing import Optional, List
from .vector_record import VectorRecord
from code_sushi.context import Context, LogLevel
from .utils import chunks
import time

class Pinecone(VectorDatabaseLayer):
    """
    Responsible for interacting with the Pinecone API for managing indexes and vector DB entries.
    """
    def __init__(self, context: Context, index_name: Optional[str] = None, pool_threads: int = 30):
        self.context = context 
        self.namespace = context.project_name

        api_key = context.pinecone_config.get("api_key")
        self.client = PineconeClient(api_key=api_key, pool_threads=pool_threads)

        if not index_name:
            index_name = context.pinecone_config.get("index_name")
        
        self.index = self.client.Index(index_name, pool_threads=pool_threads)
    
    def write(self, record: VectorRecord) -> None:
        """
        Write a single vector record to the database.
        """
        with self.index as index:
            index.upsert(
                vectors=[{
                    "id": record.key,
                    "values": record.embedding,
                    "metadata": record.metadata
                }],
                namespace=self.namespace
            )

    def write_many(self, records: List[VectorRecord], chunk_size: int = 400) -> int:
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

        if self.context.is_log_level(LogLevel.VERBOSE):
            print(f"Batch writing {len(items)} items to index, namespace {self.namespace}")

        with self.index as index:
            # Send chunked requests in parallel
            async_results = [
                index.upsert(vectors=ids_vectors_chunk, async_req=True, namespace=self.namespace)
                for ids_vectors_chunk in chunks(items, chunk_size)
            ]

            # Wait for and retrieve responses (this raises in case of error)
            res = [async_result.get() for async_result in async_results]
            
            if self.context.is_log_level(LogLevel.VERBOSE):
                runtime = time.time() - start
                print(f"Batch write finished in {runtime:.2f} seconds")

            return len(res)

    def search(self, query: List[float], top_k: int = 10, filters: Optional[dict] = None) -> List[VectorRecord]:
        """
        Search the Pinecone index for similar vectors.
        """
        with self.index as index:
            response = index.query(
                vector=query, 
                top_k=top_k, 
                namespace=self.namespace, 
                include_metadata=True,
                filter=filters
            )

            hits = []
            # Convert the response to a list of VectorRecords
            for match in response['matches']:
                metadata = match['metadata']
                metadata['id'] = match['id']
                metadata['score'] = match['score']
                hits.append(VectorRecord(
                    key=match['id'],
                    text=metadata.get('summary', ''),
                    embedding=match.get('values', []),
                    metadata=metadata
                ))
            
            if self.context.is_log_level(LogLevel.VERBOSE):
                low_score = min([hit.metadata['score'] for hit in hits])
                high_score = max([hit.metadata['score'] for hit in hits])
                print(f"RAG Search results: {len(hits)} hits from {low_score:.2f} to {high_score:.2f} scores")

            return hits
