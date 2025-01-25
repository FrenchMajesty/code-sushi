import threading
from typing import List
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
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
        self.capacity = 0
        self.state = {}

        self.prepare(files)
        print("Job queue initialized.")

        # Peek at the highest-priority item
        def peek(pq):
            with pq.mutex:  # Lock the queue for thread safety
                if pq.queue:
                    return pq.queue.pop()  # The smallest element
            return None

        print(self.queue)
    
    def prepare(self, files: List[File]):
        for priority, file in prioritize_files(files):
            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Adding {file.absolute_path} to queue with priority {priority}")
            self.push(priority, JobTask(self.context, file))

    def push(self, priority: int, job: JobTask):
        with self.lock:
            self.capacity += 1
            self.queue.put((priority, job))
            self.state[job.name] = job.status
            self.save()

    def pop(self):
        with self.lock:
            if not self.queue.empty():
                self.capacity -= 1
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
                # For example, saving the self.state to a file
                # For fault tolerance and to pick up where we left off
                # on long or interrupted processes
                pass

        threading.Thread(target=debounce_save).start()
