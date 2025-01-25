from typing import List
from collections import deque
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from code_sushi.core import write_summary
from .llm_client import summarize_file
from code_sushi.jobs import JobTask, TaskStatus
from code_sushi.core import Itamae
import time

class Agent:
    def __init__(self, context: Context, id: int):
        self.id = id
        self.context = context
        self.tasks_completed = 0

        if self.context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Agent [{self.id}] was hired and is ready to work.")

    def perform(self, task: JobTask) -> List[JobTask]:
        """
        Execute the task.
        """
        start_time = time.time()

        if self.context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Processing {task.name}...")

        self.busy = True
        self.tasks_completed += 1
        task.update_status(TaskStatus.IN_PROGRESS)

        # 1- Summarize the file content using LLM
        content = open(task.file.absolute_path).read()
        summary = summarize_file(self.context, task.file.clean_path, content)
        write_summary(self.context, task.file, summary)

        # 2- Extract logical chunks from the file
        chunks = Itamae.slice_chunks(self.context, task.file)
        # TODO: Add to queue for further summarization of the chunk

        task.update_status(TaskStatus.COMPLETE)
        self.busy = False

        if self.context.log_level.value >= LogLevel.DEBUG.value:
            runtime = time.time() - start_time
            print(f"Agent [{self.id}] Completed Job {task.name} in {runtime:.2f} seconds.")#

        return []
