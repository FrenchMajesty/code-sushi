from code_sushi.core import File
from code_sushi.repo import CodeFragment
from code_sushi.context import Context, LogLevel
from typing import Optional
from enum import Enum
import time
import os

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
    def __init__(self, context: Context, fragment: CodeFragment, file: Optional[File] = None):
        self.fragment = fragment
        self.name = fragment.name
        self.status = TaskStatus.PENDING
        self.context = context
        self.busy = False
        self.file = file

    def relative_path(self) -> str:
        return self.fragment.path

    def absolute_path(self) -> str:
        return self.fragment.absolute_path()

    def is_file(self) -> bool:
        return self.file is not None

    def is_function(self) -> bool:
        return self.fragment.parent_file_summary is not None

    def update_status(self, status: TaskStatus) -> None:
        self.status = status
    
    def __lt__(self, other: "JobTask"):
        return self.name < other.name

    def __repr__(self):
        return f"JobTask(name='{self.name}')"
