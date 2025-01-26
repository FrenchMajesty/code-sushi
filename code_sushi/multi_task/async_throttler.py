import asyncio
from typing import Callable, Awaitable, Any

class AsyncThrottler:
    """
    AsyncThrottler class for throttling async requests.
    """
    def __init__(self, max_concurrent: int = 25):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def run_with_throttle(self, coro: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Run the coroutine with throttling when we hit the max concurrent limit.
        """
        async with self.semaphore:
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                print(f"Error in throttled task: {e}")
                raise
