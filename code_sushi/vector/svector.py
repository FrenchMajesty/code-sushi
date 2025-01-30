from asyncio import sleep
from code_sushi.context import Context, LogLevel
from svectordb.client import DatabaseService
from svectordb.config import Config
from svectordb.models import *
from smithy_core.retries import SimpleRetryStrategy
from smithy_http.aio.identity.apikey import ApiKeyIdentity, ApiKeyIdentityResolver
from .vector_record import VectorRecord
from code_sushi.multi_task import AsyncThrottler, run_async_in_background

class SVector:
    """
    SVector class for interacting with the Vector Database.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, context: Context) -> None:
        self.context = context
        region = context.svector_config.get("region")
        apiKey = context.svector_config.get("api_key")
        databaseId = context.svector_config.get("database_id")

        self.client = DatabaseService(Config(
            endpoint_uri=f"https://{region}.api.svectordb.com",
            api_key_identity_resolver=ApiKeyIdentityResolver(api_key=ApiKeyIdentity(api_key=apiKey)),
            retry_strategy=SimpleRetryStrategy(max_attempts=1)
        ))
        self.throttler = AsyncThrottler(max_concurrent=25)

    def write(self, record: VectorRecord) -> None:
        run_async_in_background(self.__write_async, record)

    async def __write_async(self, record: VectorRecord):
        """
        Fire off async request to write embeddings to the Vector Database.
        """
        retries = 3
        for attempt in range(retries):
            try:
                if self.context.is_log_level(LogLevel.DEBUG):
                    print(f"Writing to Vector DB: {record.key}")
                
                await self.throttler.run_with_throttle(self.client.set_item, SetItemInput(
                    database_id=databaseId,
                    key=record.key,
                    value=record.text.encode('utf-8'),
                    vector=record.embedding,
                    metadata=self.hashmap_to_metadata(record.metadata)
                ))
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt + 1 < retries:
                    await sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Failed to write to Vector DB after {retries} attempts.")

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
