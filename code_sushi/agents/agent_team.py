from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from code_sushi.jobs import JobQueue, JobTask
from code_sushi.context import Context, LogLevel
from .agent import Agent
import time

class AgentTeam:
    def __init__(self, context: Context):
        self.context = context
        self.count = context.max_agents

    def get_to_work(self, pipeline: JobQueue):
        """
        Process the files in parallel using a team of agents.
        """
        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Starting Agent Team with {self.count} agents...")

        # Worker thread function
        def init_agent_worker(context: Context, queue: JobQueue, id: int):
            agent = Agent(context, id)
            while not queue.empty():
                _, job = queue.pop()
                if job:
                    chunk_tasks = agent.perform(job)

                    for task in chunk_tasks:
                        queue.push(5, task)

                    queue.mark_complete(job)
                else:
                    break

        def monitor_queue(queue: JobQueue):
            queue.track_start()

            while not queue.empty():
                queue.print_status_update()
                time.sleep(3)
            
            queue.track_end()
            queue.print_status_update()
            print("Queue is empty. Monitoring stopped.")

        # Manage workers using ThreadPoolExecutor
        workers = self.count
        with ThreadPoolExecutor(max_workers=workers + 1) as executor:
            for i in range(workers):
                executor.submit(init_agent_worker, self.context, pipeline, i)

            # Monitor the queue
            executor.submit(monitor_queue, pipeline)
