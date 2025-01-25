import threading
from typing import List
from code_sushi.core import File
from code_sushi.context import Context
from .utils import prioritize_files
from .job_task import JobTask, TaskStatus
from queue import PriorityQueue
import time

class JobQueue:
    """
    Responsible for managing the job queue, and the state of each job.
    """
    def __init__(self, context: Context, files: List[File]):
        self.context = context
        self.queue: PriorityQueue[tuple[int, JobTask]] = PriorityQueue()
        self.lock = threading.Lock()
        self.state = {}

        self.prepare(files)
        print("Job queue initialized.")
        print(self.queue)
    
    def prepare(self, files: List[File]):
        for file, priority in prioritize_files(files):
            self.push(priority, JobTask(file))

    def push(self, priority: int, job: JobTask):
        with self.lock:
            self.queue.put((priority, job))
            self.state[job.name] = job.status
            self.save()

    def pop(self):
        with self.lock:
            if not self.queue.empty():
                priority, job = self.queue.get()
                self.state[job.name] = job.status
                self.save()
                return priority, job
        
        return None, None

    def mark_complete(self, job: JobTask):
        with self.lock:
            self.state[job.name] = job.status
            self.save()

    def save(self):
        def debounce_save():
            time.sleep(0.2)
            with self.lock:
                # TODO: Implement the actual save logic here
                # For example, saving the state to a file or database
                # For fault tolerance and to pick up where we left off
                # on long or interrupted processes
                pass

        threading.Thread(target=debounce_save).start()
