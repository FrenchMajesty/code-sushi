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

        self.ai_provider: str = "together"
        self.vector_db_provider: str = "pinecone"
        self.max_agents: int = 10
        self.vector_db_concurrent_limit: int = 25
        self.embedding_model_chunk_size: int = 128
        self.stream_chat_response: bool = True

        # Foundation Models
        self.together_ai_config = defaultdict(str)
        self.openai_config = defaultdict(str)
        
        # Vector Databases
        self.svector_config = defaultdict(str)
        self.pinecone_config = defaultdict(str)

        # Embedding Models
        self.voyage_ai_config = defaultdict(str)

    def get_model_config(self):
        if self.ai_provider == "together":
            return self.together_ai_config
        elif self.ai_provider == "openai":
            return self.openai_config
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
    
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

    def overview(self):
        """
        Return a dictionary containing an overview of non-config context properties.
        """
        return {
            "repo_path": self.repo_path,
            "log_level": self.log_level,
            "output_dir": self.output_dir,
            "project_name": self.project_name,
            "has_config_file": self.has_config_file,
            "ai_provider": self.ai_provider,
            "vector_db_provider": self.vector_db_provider,
            "max_agents": self.max_agents,
            "vector_db_concurrent_limit": self.vector_db_concurrent_limit,
            "embedding_model_chunk_size": self.embedding_model_chunk_size,
            "stream_chat_response": self.stream_chat_response
        }
