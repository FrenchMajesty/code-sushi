from typing import Optional
from enum import Enum
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

    def get_files_in_output_dir(self):
        """
        Get all the files in the output directory.
        """
        return [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.output_dir) for f in filenames]
