import asyncio
import random
import os

from svectordb.client import DatabaseService
from svectordb.config import Config
from svectordb.models import *
from smithy_core.retries import SimpleRetryStrategy
from smithy_http.aio.identity.apikey import ApiKeyIdentity, ApiKeyIdentityResolver
from dotenv import load_dotenv
from typing import List


load_dotenv()

region = os.getenv('SVECTOR_REGION')
apiKey = os.getenv('SVECTOR_API_KEY')
databaseId = os.getenv('SVECTOR_DATABASE_ID')

class SVector:
    """
    SVector class for interacting with the Vector Database.
    """

    def __init__(self) -> None:
        self.client = DatabaseService(Config(
            endpoint_uri=f"https://{region}.api.svectordb.com",
            api_key_identity_resolver=ApiKeyIdentityResolver(api_key=ApiKeyIdentity(api_key=apiKey)),
            retry_strategy=SimpleRetryStrategy(max_attempts=1)
        ))

    def write(self, key: str, vector: List[float], summary: str, metadata: dict = {}) -> None:
        """
        Write embeddings to the Vector Database.
        """

        self.client.set_item(SetItemInput(
            database_id=databaseId,
            key=key,
            value=summary.encode('utf-8'),
            vector=vector,
            metadata=self.hashmap_to_metadata(metadata)
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
