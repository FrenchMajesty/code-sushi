from typing import List
from code_sushi.context import Context, LogLevel
from code_sushi.core import write_summary_to_file, File
from code_sushi.jobs import JobTask, TaskStatus
from code_sushi.itamae import Itamae
from .llm_client import summarize_file
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

        try:
            tasks = []
            self.busy = True
            self.tasks_completed += 1
            task.update_status(TaskStatus.IN_PROGRESS)

            # 1- Summarize the file content using LLM
            origin_file = task.absolute_path()
            content = open(origin_file).read()
            summary = summarize_file(self.context, task.relative_path(), content)
            write_summary_to_file(self.context, task.file, summary)

            if task.is_file():
                # 2- Extract logical chunks from the file
                chunks = Itamae().slice_chunks(self.context, task.file)
                for chunk in chunks:
                    # Create a new task for each chunk
                    temp_file = File(self.context.repo_path, chunk.absolute_path)
                    temp_file.absolute_path = chunk.absolute_path
                    temp_file.clean_path = chunk.relative_path

                    task = JobTask(self.context, chunk=chunk, file=temp_file)
                    tasks.append(task)

            task.update_status(TaskStatus.COMPLETE)
            self.busy = False

            if self.context.log_level.value >= LogLevel.DEBUG.value:
                runtime = time.time() - start_time
                print(f"Agent [{self.id}] Completed Job {task.name} in {runtime:.2f} seconds.")#

            return tasks
        except Exception as e:
            task.update_status(TaskStatus.FAILED)
            self.busy = False
            print(f"Agent [{self.id}] Failed Job {task.name}. Error: {e}")
            return []
