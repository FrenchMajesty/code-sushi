from code_sushi.core import File
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
    def __init__(self, file: File):
        self.file = file
        self.name = file.absolute_path
        self.status = TaskStatus.PENDING
        self.busy = False

    def execute(self):
        """
        Execute the task.
        """
        self.busy = True
        self.status = TaskStatus.IN_PROGRESS

        time.sleep(2)
        # Read the file
        # Process the file
        # Store the results
        # Return the results
    
        self.status = TaskStatus.COMPLETE
        self.busy = False
