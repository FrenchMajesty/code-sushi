from typing import List
from code_sushi.context import Context, LogLevel
from code_sushi.core import write_summary_to_file, File
from code_sushi.jobs import JobTask, TaskStatus
from code_sushi.itamae import Itamae, LogicalChunk
from .llm_client import summarize_file
import time

class Agent:
    def __init__(self, context: Context, id: int):
        self.id = id
        self.context = context
        self.tasks_completed = 0

        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Agent [{self.id}] was hired and is ready to work.")

    def perform(self, task: JobTask) -> List[JobTask]:
        """
        Execute the task.
        """
        start_time = time.time()

        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Performing task {task.name}...", task.file.relative_path)

        try:
            tasks = []
            self.busy = True
            task.update_status(TaskStatus.IN_PROGRESS)

            summary = self.summarize_content(task)
            if task.is_file():
                # 2- Extract logical chunks from the file
                chunks = Itamae().slice_chunks(self.context, task.file)
                tasks = self.chunks_to_tasks(chunks, summary)

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
    
    def summarize_content(self, task: JobTask) -> str:
        """
        Summarize the content of a file using LLM.
        """
        try:
            origin_file = task.absolute_path()
            content = open(origin_file).read()
            parent_summary = task.chunk.parent_summary if task.chunk else ""

            summary = summarize_file(self.context, task.relative_path(), content, parent_summary)
            write_summary_to_file(self.context, task.file, summary)

            return summary
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return ""

    def chunks_to_tasks(self, chunks: List[LogicalChunk], summary: str) -> List[JobTask]:
        """
        Convert a list of logical chunks into a list of JobTasks.
        """
        if self.context.is_log_level(LogLevel.VERBOSE):
            print(f"Converting {len(chunks)} chunks into tasks...")

        tasks = []
        for chunk in chunks:
            temp_file = File(self.context.repo_path, chunk.absolute_path)
            temp_file.absolute_path = chunk.absolute_path
            temp_file.relative_path = chunk.relative_path

            if ".llm/Users" in temp_file.relative_path:
                print('BAD PATH! in chunks_to_tasks()')
                exit(1)

            chunk.parent_summary = summary

            task = JobTask(self.context, chunk=chunk, file=temp_file)
            tasks.append(task)

        return tasks
