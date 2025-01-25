from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from code_sushi.jobs import JobQueue, JobTask
from code_sushi.context import Context, LogLevel
import time

class AgentTeam:
    def __init__(self, context: Context, agent_count: int = 10):
        self.context = context
        self.count = agent_count

    def get_to_work(self, pipeline: JobQueue):
        """
        Process the files in parallel using a team of agents.
        """
        if self.context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Starting Agent Team with {self.count} agents...")

        # Chunk the files into equal parts
        # Distribute the chunks to the agents
        # Agents process the chunks in parallel
        # Store the results in the output directory
        # Wait for all agents to finish processing

        # Initialize queue and push tasks
        # Simulate file processing
        def process_job(job: JobTask, queue: JobQueue):
            job.execute()
            queue.mark_complete(job)

        # Worker thread function
        def worker(queue: JobQueue):
            while not queue.empty():
                _, job = queue.pop()
                if job:
                    process_job(job, queue)
                else:
                    break
        

        def monitor_queue(queue: JobQueue):
            while not queue.empty():
                queue.print_status_update()
                time.sleep(5)
            print("Queue is empty. Monitoring stopped.")

        # Manage workers using ThreadPoolExecutor
        workers = self.count // 2
        with ThreadPoolExecutor(max_workers=workers + 1) as executor:
            executor.submit(monitor_queue, pipeline)

            for _ in range(workers):
                executor.submit(worker, pipeline)
