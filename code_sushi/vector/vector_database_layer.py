from abc import ABC, abstractmethod
from typing import List, Optional
from .vector_record import VectorRecord

class VectorDatabaseLayer(ABC):
    """
    Abstract base class defining the interface for vector database operations.
    All vector database implementations (Pinecone, SVector, etc.) should implement this interface.
    """

    @abstractmethod
    def write(self, record: VectorRecord) -> None:
        """
        Write a single vector record to the database.
        
        Args:
            record: VectorRecord containing the embedding and metadata to store
        """
        pass

    @abstractmethod
    def write_many(self, records: List[VectorRecord], chunk_size: int = 400) -> int:
        """
        Write multiple vector records to the database in batch.
        
        Args:
            records: List of VectorRecords to store
            chunk_size: Size of chunks to break requests into
            
        Returns:
            Number of records successfully written
        """
        pass

    @abstractmethod
    def search(self, query: List[float], top_k: int = 10, filters: Optional[dict] = None) -> List[VectorRecord]:
        """
        Search for similar vectors in the database.
        
        Args:
            query: Vector to search for
            top_k: Number of results to return
            filters: Optional metadata filters to apply
            
        Returns:
            List of matching records
        """
        pass
