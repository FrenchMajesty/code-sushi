import asyncio
from concurrent.futures import Future
from threading import Thread, Event
import atexit

class BackgroundLoop:
    """
    Manages an asyncio event loop running in a background thread.
    """
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.shutdown_event = Event()
        self.is_running = False
        self.thread = Thread(target=self._background_loop, daemon=True)

    def _background_loop(self):
        """Internal method that runs the event loop in the background thread."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        except Exception as e:
            print(f"Error in background loop: {e}")
        finally:
            self.loop.close()

    def start(self):
        """Start the background event loop thread."""
        self.thread.start()
        self.is_running = True

    def stop(self):
        """Stop the background event loop."""
        atexit.register(self._stop_on_exit)

    def _stop_on_exit(self):
        """
        Stop the background event loop on exit.
        """
        self.shutdown_event.set()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.is_running = False

    def run_async(self, coro_func, *args, **kwargs) -> Future:
        """
        Run an async function in the background without awaiting it.
        Suitable for fire-and-forget tasks from synchronous code.
        Returns the created Task object for tracking completion.
        """
        if not self.loop.is_running():
            raise RuntimeError("Background event loop is not running.")
        
        # Create the coroutine
        coro = coro_func(*args, **kwargs)
        # Create and return a Task instead of just scheduling it
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

# Create singleton instance
background_loop = BackgroundLoop()
