from asyncio import sleep
from code_sushi.context import Context, LogLevel
from svectordb.client import DatabaseService
from svectordb.config import Config
from svectordb.models import *
from smithy_core.retries import SimpleRetryStrategy
from smithy_http.aio.identity.apikey import ApiKeyIdentity, ApiKeyIdentityResolver
from typing import Optional, List
from .vector_record import VectorRecord
from code_sushi.multi_task import AsyncThrottler, background_loop
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
            api_key_identity_resolver=ApiKeyIdentityResolver(ApiKeyIdentity(api_key)),
            retry_strategy=SimpleRetryStrategy(max_attempts=3)
        ))
        self.throttler = AsyncThrottler(max_concurrent=context.vector_db_max_concurrent_requests)

    def write(self, record: VectorRecord) -> None:
        """Write a single vector record"""
        background_loop.run_async(self.__write_async, record)

    def write_many(self, records: List[VectorRecord], chunk_size: int = 400) -> int:
        """Write multiple vector records in chunks"""
        for record in records:
            self.write(record)
        return len(records)

    def search(self, query: List[float], top_k: int = 10, filters: Optional[dict] = None) -> List[VectorRecord]:
        """Search for similar vectors"""
        raise NotImplementedError("Search not yet implemented for Svector")

    async def __write_async(self, record: VectorRecord):
        """
        Fire off async request to write embeddings to the Vector Database.
        """
        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Writing to Vector DB: {record.key}")
        
        await self.throttler.run_with_throttle(self.client.set_item, SetItemInput(
            database_id=self.database_id,
            key=record.key,
            value=record.text.encode('utf-8'),
            vector=record.embedding,
            metadata=self.hashmap_to_metadata(record.metadata)
        ))

    def hashmap_to_metadata(self, hashmap: dict) -> dict:
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
