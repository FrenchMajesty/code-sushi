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

        # Track run time
        self.start_time = None
        self.end_time = None
        self.duration = None

        self.prepare(files)

        if self.context.is_log_level(LogLevel.DEBUG):
            print("Job queue initialized.")
            print("Top priority job:", peek(self.queue))
    
    def track_start(self):
        """
        Track the start time of the job queue.
        """
        self.start_time = time.time()

    def track_end(self):
        """
        Track the end time of the job queue.
        """
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def prepare(self, files: List[File]):
        for priority, file in prioritize_files(files):
            if file.size == 0:
                continue

            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Adding {file.absolute_path} to queue with priority {priority}")
            self.push(priority, JobTask(self.context, file))

    def push(self, priority: int, job: JobTask):
        with self.lock:
            self.capacity += 1
            self.queue.put((-priority, job))
            self.state[job.name] = TaskStatus.IN_PROGRESS
            self.save()

    def pop(self):
        with self.lock:
            if not self.queue.empty():
                self.capacity -= 1
                priority, job = self.queue.get()
                self.state[job.name] = TaskStatus.IN_PROGRESS
                self.save()
                if self.context.is_log_level(LogLevel.VERBOSE):
                    print(f"Popped {job.name} from queue to begin work.")
                return priority, job
        
        return None, None

    def empty(self):
        with self.lock:
            return self.queue.empty()

    def mark_complete(self, job: JobTask):
        with self.lock:
            self.state[job.name] = TaskStatus.COMPLETE
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
    
    def print_status_update(self):
        """
        Print the current status of the job queue with a more visually pleasing format.
        """
        pending_count = sum(1 for status in self.state.values() if status == TaskStatus.IN_PROGRESS)
        completed_count = sum(1 for status in self.state.values() if status == TaskStatus.COMPLETE)
        total_count = len(self.state)

        # Calculate percentages
        completed_percent = (completed_count / total_count) * 100 if total_count else 0
        pending_percent = (pending_count / total_count) * 100 if total_count else 0

        # Generate progress bar
        bar_width = 30
        completed_blocks = int((completed_count / total_count) * bar_width) if total_count else 0
        pending_blocks = int((pending_count / total_count) * bar_width) if total_count else 0

        progress_bar = "[" + "#" * completed_blocks + "-" * (bar_width - completed_blocks) + "]"

        # Print the status
        print("\n" + "=" * 40)
        print("            Code Sushi - Status")
        print("=" * 40)
        print(f"Total Jobs:         {total_count}")
        print(f"Pending:            {pending_count} ({pending_percent:.1f}%)")
        print(f"Completed:          {completed_count} ({completed_percent:.1f}%)")
        print(f"Progress:           {progress_bar}")

        if self.duration:
            print(f"Duration:           {self.duration:.2f} seconds")

        print("=" * 40)

def peek(pq):
    """
    Peek at the highest-priority item in the queue.
    """
    with pq.mutex:  # Lock the queue for thread safety
        if pq.queue:
            return pq.queue[0]  # The largest element (max-heap with negated priorities)
    return None
