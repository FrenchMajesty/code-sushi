from typing import List
from datetime import datetime, timezone

class VectorRecord:
    """
    Represents a record already stored or to-be stored in our Vector DB.
    """
    def __init__(self, key: str, text: str, metadata: dict = {}, embedding: List[float] = []):
        self.key: str = key
        self.text: str = text
        self.metadata: dict = metadata
        self.embedding: List[float] = embedding
        self.score: float = 0.0
    
    @staticmethod
    def from_files(files: List[str], project_name: str) -> List["VectorRecord"]:
        """
        Create vector records from file paths.
        
        Args:
            files: List of file paths to process
            project_name: Name of the project
            
        Returns:
            List of VectorRecord objects
        """
        entries = []
        for file_path in files:
            try:
                file_meta = extract_metadata_from_output_file(file_path)
                if not file_meta:
                    continue

                key = f"{project_name}/{file_meta['file']}".replace('//', '/')
                last_updated = datetime.now(timezone.utc).isoformat() + 'Z'
                
                metadata = {
                    "summary": file_meta['summary'],
                    "original_location": file_meta['file'], 
                    "last_updated": last_updated,
                    "project_name": project_name,
                    "type": "function" if "@" in file_meta['file'] else "file"
                }
                # Strip metadata that are null
                metadata = {k: v for k, v in metadata.items() if v is not None}

                entries.append(VectorRecord(key, file_meta['summary'], metadata))
                
            except Exception as e:
                print(f"Failed in VectorRecord.create_from_files() for {file_path}. Error: {e}")
                
        return entries
