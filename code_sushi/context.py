from typing import Optional
from enum import Enum

class LogLevel(Enum):
    NONE = 0
    INFO = 1
    DEBUG = 2
    VERBOSE = 3


class Context:
    def __init__(self, repo_path: Optional[str] = None, log_level: int = 1):
        self.repo_language: Optional[str] = None
        self.repo_path: Optional[str] = repo_path
        self.log_level: LogLevel = LogLevel(log_level)
