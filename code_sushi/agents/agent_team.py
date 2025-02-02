from typing import List, Optional
from code_sushi.jobs import JobQueue
from code_sushi.types import JobTask
from code_sushi.context import Context, LogLevel
from code_sushi.multi_task import WorkerPool
from .agent import Agent
import time

class AgentTeam:
    def __init__(self, context: Context):
        self.context = context
        self.count = context.max_agents
        self.fragments_done = {}

    def get_to_work(self, pipeline: JobQueue):
        """
        Process the files in parallel using a team of agents.
        """
        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Starting Agent Team with {self.count} agents...")


        # Use WorkerPool to manage workers
        worker_pool = WorkerPool(self.count + 1)  # +1 for monitor thread
        
        # Start worker threads
        for i in range(self.count):
            worker_pool.submit(self._init_agent_worker, self.context, pipeline, i)

        # Start monitor thread
        worker_pool.submit(self._monitor_queue, pipeline)
        
        # Wait for all work to complete
        worker_pool.wait_all()

    def _init_agent_worker(self, context: Context, queue: JobQueue, id: int):
        """
        Initialize an agent worker.
        """
        agent = Agent(context, id)
        while not queue.empty():
            _, job = queue.pop()
            if job:
                chunk_tasks = agent.perform(job)

                for task in chunk_tasks:
                    queue.push(5, task)

                queue.mark_complete(job)
                self.fragments_done[job.fragment.name] = job.fragment
            else:
                break

    def _monitor_queue(self, queue: JobQueue):
        """
        Monitor the queue for progress.
        """
        queue.track_start()

        while not queue.empty():
            queue.print_status_update()
            time.sleep(3)
        
        queue.track_end()
        queue.print_status_update()
        print("Queue is empty. Monitoring stopped.")
