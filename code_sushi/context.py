from typing import Optional
from enum import Enum
from collections import defaultdict
import os

class LogLevel(Enum):
    NONE = 0
    INFO = 1
    DEBUG = 2
    VERBOSE = 3


class Context:
    def __init__(self, repo_path: Optional[str] = None, log_level: int = 1):
        self.repo_path: Optional[str] = repo_path
        self.log_level: LogLevel = LogLevel(log_level)
        self.output_dir: Optional[str] = None
        self.project_name: str = os.path.basename(repo_path)
        self.has_config_file: bool = False

        self.max_agents: int = 10
        self.blob_storage_concurrent_limit: int = 25
        self.vector_db_concurrent_limit: int = 25
        self.embedding_model_chunk_size: int = 128

        self.together_ai_config = defaultdict(str)
        self.voyage_ai_config = defaultdict(str)
        self.svector_config = defaultdict(str)
        self.pinecone_config = defaultdict(str)

    def get_files_in_output_dir(self):
        """
        Get all the files in the output directory.
        """
        return [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.output_dir) for f in filenames]

    def is_log_level(self, level: LogLevel):
        """
        Check if the current log level is greater or equal to the given level.
        """
        return self.log_level.value >= level.value
