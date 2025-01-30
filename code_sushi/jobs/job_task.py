from code_sushi.core import File
from code_sushi.itamae import CodeFragment
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
    def __init__(self, context: Context, file: Optional[File] = None, fragment: Optional[CodeFragment] = None):
        self.file = file
        self.fragment = fragment
        self.status = TaskStatus.PENDING
        self.context = context
        self.busy = False

        if fragment:
            self.name = fragment.name
        elif file:
            self.name = file.relative_path
        else:
            raise ValueError("A JobTask must have a file or a code fragment.")

    def relative_path(self) -> str:
        return self.fragment.path if self.fragment else self.file.relative_path

    def absolute_path(self) -> str:
        return self.fragment.path if self.fragment else self.file.absolute_path

    def update_status(self, status: TaskStatus):
        self.status = status

    def is_fragment(self) -> bool:
        return self.fragment is not None
    
    def is_file(self) -> bool:
        return self.file is not None

    def __lt__(self, other: "JobTask"):
        return self.name < other.name

    def __repr__(self):
        return f"JobTask(name='{self.name}')"
