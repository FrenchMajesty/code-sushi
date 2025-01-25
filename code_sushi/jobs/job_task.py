from code_sushi.core import File
from code_sushi.context import Context, LogLevel
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
    def __init__(self, context: Context, file: File):
        self.file = file
        self.name = file.clean_path
        self.status = TaskStatus.PENDING
        self.context = context
        self.busy = False

    def execute(self):
        """
        Execute the task.
        """
        start_time = time.time()
        if self.context.log_level.value >= LogLevel.VERBOSE.value:
            print(f"Processing {self.name}...")

        self.busy = True
        self.status = TaskStatus.IN_PROGRESS

        time.sleep(2)

        # TODO: Read the file
        # Process the file
        # Store the results
        # Return the results

        self.status = TaskStatus.COMPLETE
        self.busy = False

        if self.context.log_level.value >= LogLevel.VERBOSE.value:
            runtime = time.time() - start_time
            print(f"Completed {self.name} Job in {runtime:.2f} seconds.")

    def __lt__(self, other: "JobTask"):
        return self.name < other.name

    def __repr__(self):
        return f"JobTask(name='{self.name}')"
