from typing import List, Optional
from code_sushi.context import Context, LogLevel
from .vector_record import VectorRecord
from .vector_database_layer import VectorDatabaseLayer
from .pinecone import Pinecone
from .svector import SVector

class VectorClient:
    """
    High-level client for interacting with vector databases.
    Uses context configuration to determine which vector DB implementation to use.
    """
    SUPPORTED_PROVIDERS = {
        "pinecone": Pinecone,
        "svector": SVector
    }

    def __init__(self, context: Context):
        """
        Initialize vector client with configuration from context.
        
        Args:
            context: Application context containing vector DB config
        """
        self.context = context
        self.provider = context.vector_db_provider
         
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported vector DB provider: {self.provider}")
            
        self.client: VectorDatabaseLayer = self.SUPPORTED_PROVIDERS[self.provider](context)

    def write(self, record: VectorRecord) -> None:
        """
        Write a single vector record to the database.
        
        Args:
            record: VectorRecord to store
        """
        self.client.write(record)

    def write_many(self, records: List[VectorRecord], chunk_size: int = 400) -> int:
        """
        Write multiple vector records to the database.
        
        Args:
            records: List of VectorRecords to store
            chunk_size: Size of chunks for batched writes
            
        Returns:
            Number of records written
        """
        return self.client.write_many(records, chunk_size)

    def search(self, query: List[float], top_k: int = 10, filters: Optional[dict] = None) -> List[VectorRecord]:
        """
        Search for similar vectors in the database.
        
        Args:
            query: Vector to search for
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of matching VectorRecords
        """
        return self.client.search(query, top_k, filters)
