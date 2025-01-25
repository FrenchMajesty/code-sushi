from typing import List
from collections import deque
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from .llm_client import summarize_file
from code_sushi.jobs import JobTask, TaskStatus
import time

class Agent:
    def __init__(self, context: Context, id: int):
        self.id = id
        self.context = context
        self.tasks_completed = 0

        if self.context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Agent [{self.id}] was hired and is ready to work.")

    def perform(self, task) -> List[JobTask]:
        """
        Execute the task.
        """
        start_time = time.time()

        if self.context.log_level.value >= LogLevel.VERBOSE.value:
            print(f"Processing {task.name}...")

        self.busy = True
        self.tasks_completed += 1
        #task.update_status(TaskStatus.IN_PROGRESS)

        time.sleep(1)
        # Read file content from disk
        #content = open(task.file.absolute_path).read()
        #summary = summarize_file(task.file.clean_path, content)
        #exit(0)
        #raise Exception("Test exception to stop execution")

        # TODO: Use LLM to extract functions or logical blocks
        # TODO: Generate a summary of the file in parallel.
        # TODO: Store the results in the output directory
        # Return the results

        #- each will then summarize the file as whole and in parallel get it chunked up
        #- once chunked up, it will queue it up for processing

        #task.update_status(TaskStatus.COMPLETE)
        self.busy = False

        if self.context.log_level.value >= LogLevel.VERBOSE.value:
            runtime = time.time() - start_time
            print(f"Agent [{self.id}] Completed Job {task.name} in {runtime:.2f} seconds.")#

        return []
