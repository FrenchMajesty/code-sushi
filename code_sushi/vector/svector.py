from asyncio import sleep
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from code_sushi.context import Context, LogLevel
from svectordb.client import DatabaseService
from svectordb.config import Config
from svectordb.models import *
from smithy_core.retries import SimpleRetryStrategy
from smithy_http.aio.identity.apikey import ApiKeyIdentity, ApiKeyIdentityResolver
from typing import Optional, List
from code_sushi.types import VectorRecord
from code_sushi.multi_task import background_loop, WorkerPool
from .vector_database_layer import VectorDatabaseLayer

class SVector(VectorDatabaseLayer):
    """
    Svector class for interacting with the Vector Database.
    """
    def __init__(self, context: Context) -> None:
        self.context = context
        region = context.svector_config.get("region")
        api_key = context.svector_config.get("api_key") 
        self.database_id = context.svector_config.get("database_id")

        self.client = DatabaseService(Config(
            endpoint_uri=f"https://{region}.api.svectordb.com",
            api_key_identity_resolver=ApiKeyIdentityResolver(api_key=ApiKeyIdentity(api_key=api_key)),
            retry_strategy=SimpleRetryStrategy(max_attempts=3)
        ))
        self.worker_pool = WorkerPool(max_workers=context.vector_db_concurrent_limit)

    def write(self, record: VectorRecord) -> None:
        """Write a single vector record"""
        self.worker_pool.submit(self._write_sync, record)

    def write_many(self, records: List[VectorRecord], chunk_size: int = 400) -> int:
        """Write multiple vector records in chunks"""
        for record in records:
            self.worker_pool.submit(self._write_sync, record)
        
        try:
            self.worker_pool.wait_all()
        except Exception as e:
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Failed to write records: {e}")
            raise
        
        return len(records)

    def search(self, query: List[float], top_k: int = 10, filters: Optional[dict] = None) -> List[VectorRecord]:
        """Search for similar vectors"""
        raise NotImplementedError("Search not yet implemented for Svector")

    def _write_sync(self, record: VectorRecord):
        """
        Synchronous wrapper for writing embeddings to the Vector Database.
        """
        try:
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Writing to Vector DB: {record.key}")
            
            # Create the input object
            input_obj = SetItemInput(
                database_id=self.database_id,
                key=record.key,
                value=record.text.encode('utf-8'),
                vector=record.embedding,
                metadata=self._hashmap_to_metadata(record.metadata)
            )
            
            # Run the async operation in the background loop
            future = background_loop.run_async(self.client.set_item, input_obj)
            result = future.result()  # Wait for completion
            
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Completed write to Vector DB: {record.key}")
            
            return result
        except Exception as e:
            print(f"Error writing to Vector DB for key {record.key}: {e}")
            raise

    def _hashmap_to_metadata(self, hashmap: dict) -> dict:
        """
        Convert a hashmap to metadata.
        """
        metadata = {}
        for key, value in hashmap.items():
            if isinstance(value, str):
                metadata[key] = MetadataValueString(value=value)
            elif isinstance(value, int):
                metadata[key] = MetadataValueNumber(value=value)
            elif isinstance(value, list):
                metadata[key] = MetadataValueStringArray(value=value)
        return metadata
