from typing import List, Optional
from code_sushi.context import Context, LogLevel
from code_sushi.core import write_summary_to_file, File
from code_sushi.jobs import JobTask, TaskStatus
from code_sushi.itamae import Itamae
from code_sushi.repo import CodeFragment
from .model_client import ModelClient
import os
import time

class Agent:
    def __init__(self, context: Context, id: int):
        self.id = id
        self.context = context
        self.tasks_completed = 0
        self.model_client = ModelClient(context)

        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Agent [{self.id}] was hired and is ready to work.")

    def perform(self, task: JobTask) -> List[JobTask]:
        """
        Execute the task.
        """
        start_time = time.time()

        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Performing task [{task.name}] at {task.relative_path()}")

        try:
            tasks = []
            self.busy = True
            task.update_status(TaskStatus.IN_PROGRESS)

            summary = self.summarize_content(task)
            task.fragment.summary = summary

            if task.is_file():
                fragments = Itamae(self.context).slice(task.file)
                tasks = self._fragments_to_tasks(fragments, summary)

            task.update_status(TaskStatus.COMPLETE)
            self.busy = False
            self.tasks_completed += 1

            if self.context.is_log_level(LogLevel.DEBUG):
                runtime = time.time() - start_time
                print(f"Agent [{self.id}] Completed Job {task.name} in {runtime:.2f} seconds.")#

            return tasks
        except Exception as e:
            task.update_status(TaskStatus.FAILED)
            self.busy = False
            print(f"Agent [{self.id}] Failed Job {task.name}. Error: {e}")
            return []
    
    def summarize_content(self, task: JobTask) -> Optional[str]:
        """
        Summarize the content of a code fragment using LLM.
        """
        try:
            content = task.fragment.content

            if not content and task.is_file():
                content = open(task.absolute_path()).read()

            if not content:
                return None

            return self.model_client.summarize(task.relative_path(), content, task.fragment.parent_file_summary)
        except Exception as e:
            print(f"Error in Agent[{self.id}].summarize_content(): {e}")
            return None

    def _fragments_to_tasks(self, fragments: List[CodeFragment], parent_summary: str) -> List[JobTask]:
        """
        Convert a list of code fragments into a list of JobTasks.
        """
        tasks = []
        for fragment in fragments:
            fragment.parent_file_summary = parent_summary
            task = JobTask(self.context, fragment)
            tasks.append(task)

        return tasks
