from code_sushi.core import File
from code_sushi.itamae import LogicalChunk
from code_sushi.context import Context, LogLevel
from typing import Optional
from enum import Enum
import time

class TaskStatus(Enum):
    """
    Represents the status of a task.
    """
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETE = 3

class JobTask:
    """
    Represents a task to be executed.
    """
    def __init__(self, context: Context, file: Optional[File] = None, chunk: Optional[LogicalChunk] = None):
        self.file = file
        self.chunk = chunk
        self.status = TaskStatus.PENDING
        self.context = context
        self.busy = False

        if file:
            self.name = file.clean_path
        elif chunk:
            self.name = chunk.name
        else:
            raise ValueError("A JobTask must have a file or a chunk.")

    def relative_path(self):
        return self.file.clean_path if self.file else self.chunk.relative_path

    def update_status(self, status: TaskStatus):
        self.status = status

    def is_chunk(self):
        return self.chunk is not None
    
    def is_file(self):
        return self.file is not None

    def __lt__(self, other: "JobTask"):
        return self.name < other.name

    def __repr__(self):
        return f"JobTask(name='{self.name}')"
