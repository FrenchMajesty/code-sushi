import asyncio
import random
import os

from code_sushi.context import Context, LogLevel
from svectordb.client import DatabaseService
from svectordb.config import Config
from svectordb.models import *
from smithy_core.retries import SimpleRetryStrategy
from smithy_http.aio.identity.apikey import ApiKeyIdentity, ApiKeyIdentityResolver
from dotenv import load_dotenv
from typing import List
from .vector_record import VectorRecord
from code_sushi.core import run_async_in_background

load_dotenv()

region = os.getenv('SVECTOR_REGION')
apiKey = os.getenv('SVECTOR_API_KEY')
databaseId = os.getenv('SVECTOR_DATABASE_ID')

class SVector:
    """
    SVector class for interacting with the Vector Database.
    """
    def __init__(self, context: Context) -> None:
        self.context = context
        self.client = DatabaseService(Config(
            endpoint_uri=f"https://{region}.api.svectordb.com",
            api_key_identity_resolver=ApiKeyIdentityResolver(api_key=ApiKeyIdentity(api_key=apiKey)),
            retry_strategy=SimpleRetryStrategy(max_attempts=1)
        ))


    def write(self, record: VectorRecord) -> None:
        """
        """
        run_async_in_background(self.write_async, record)

    async def write_async(self, record: VectorRecord):
        """
        Fire off async request to write embeddings to the Vector Database.
        """
        try:
            task = self.client.set_item(SetItemInput(
                database_id=databaseId,
                key=record.key,
                value=record.text.encode('utf-8'),
                vector=record.embedding,
                metadata=self.hashmap_to_metadata(record.metadata)
            ))

            if self.context.log_level.value >= LogLevel.DEBUG.value:
                print(f"Writing to Vector DB: {record.key}")
            
            return task
        except Exception as e:
            print(f"Error writing to Vector DB: {e}")
    

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
