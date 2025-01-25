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
    def __init__(self, 
                context: Context, 
                file: Optional[File] = None,
                chunk: Optional[LogicalChunk] = None
                ):
        self.file = file
        self.name = file.clean_path
        self.status = TaskStatus.PENDING
        self.context = context
        self.busy = False

    def update_status(self, status: TaskStatus):
        self.status = status

    def __lt__(self, other: "JobTask"):
        return self.name < other.name

    def __repr__(self):
        return f"JobTask(name='{self.name}')"
