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
    Class for interacting with the API of SVectorDB to perform vector database operations.
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
        """
        Write a single vector record.
        """
        self.worker_pool.submit(self._write_sync, record)

    def write_many(self, records: List[VectorRecord], chunk_size: int = 400) -> int:
        """
        Write multiple vector records in chunks.
        """
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
        """
        Search for similar vectors.
        """
        try:
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Searching Vector DB with top_k={top_k}")

            # Create query input
            if not filters:
                filters = {}

            filters = filters | { 'project_name': self.context.project_name }
            filter = self._metadata_to_filter_string(filters)
            input_obj = QueryInput(
                database_id=self.database_id,
                query=QueryTypeVector(query),
                max_results=top_k,
                filter=filter
            )

            # Run query in background loop and wait for results
            background_loop.start()
            future = background_loop.run_async(self.client.query, input_obj)
            results = future.result()
            results = results.results

            # Convert results to VectorRecords
            records = []
            for item in results:
                record = VectorRecord(
                    key=item.key,
                    text=item.value.decode('utf-8'),
                    metadata=self._svector_format_to_hashmap(item.metadata)
                )
                records.append(record)

            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Found {len(records)} matching records")

            background_loop.stop()
            return records

        except Exception as e:
            print(f"Error in SVector.search(): {e}")
            raise
    def _write_sync(self, record: VectorRecord):
        """
        Synchronous wrapper for writing embeddings to the Vector Database.
        """
        try:
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Writing to Vector DB: {record.key}")
            
            # Create the input object
            metadata = self._hashmap_to_svector_format(record.metadata)
            input_obj = SetItemInput(
                database_id=self.database_id,
                key=record.key,
                value=record.text.encode('utf-8'),
                vector=record.embedding,
                metadata=metadata
            )
            
            # Run the async operation in the background loop
            future = background_loop.run_async(self.client.set_item, input_obj)
            result = future.result()  # Wait for completion
            
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Completed write to Vector DB: {record.key}")
            
            return result
        except Exception as e:
            print(f"Error in SVector._write_sync(): {e}")
            raise

    def _hashmap_to_svector_format(self, hashmap: dict) -> dict:
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

    def _svector_format_to_hashmap(self, metadata: dict) -> dict:
        """
        Convert metadata from SVector format back to a regular hashmap.
        """
        hashmap = {}
        for key, value in metadata.items():
            if hasattr(value, 'value'):
                hashmap[key] = value.value
        return hashmap
        
    def _metadata_to_filter_string(self, metadata: dict) -> str:
        """
        Convert metadata dictionary to Lucene/OpenSearch filter query string.
        
        Example:
            {"type": "python", "lines": 100} -> 'type:"python" AND lines:100'
        """
        if not metadata:
            return ""
            
        filters = []
        for key, value in metadata.items():
            if isinstance(value, str):
                filters.append(f'{key}:"{value}"')
            elif isinstance(value, (int, float)):
                filters.append(f'{key}:{value}')
            elif isinstance(value, list):
                # For arrays, match if any value matches
                values = [f'"{v}"' if isinstance(v, str) else str(v) for v in value]
                filters.append(f'{key}:({" OR ".join(values)})')
                
        return " AND ".join(filters)
