from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, List, Any
from threading import Lock

class WorkerPool:
    """
    WorkerPool class for managing a thread pool and executing tasks.
    """
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: List[Future] = []
        self._lock = Lock()

    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        """
        Submit a task to be executed by the worker pool.
        Returns the Future object representing the task.
        """
        future = self.executor.submit(fn, *args, **kwargs)
        with self._lock:
            self.futures.append(future)
        return future

    def wait_all(self) -> List[Any]:
        """
        Wait for all submitted tasks to complete and return their results.
        Any exceptions raised by tasks will be re-raised.
        """
        results = []
        exceptions = []

        with self._lock:
            # Get current futures and clear the list
            futures = self.futures.copy()
            self.futures.clear()

        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                exceptions.append(e)

        if exceptions:
            raise Exception(f"Failed to complete {len(exceptions)} tasks: {exceptions}")

        return results

    def shutdown(self, wait: bool = True):
        """
        Shutdown the worker pool. If wait=True, waits for pending tasks to complete.
        """
        self.executor.shutdown(wait=wait)
