import asyncio
from threading import Thread, Event

# Initialize the background loop
loop = asyncio.new_event_loop()
shutdown_event = Event()
def background_loop():
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    except Exception as e:
        print(f"Error in background loop: {e}")
    finally:
        loop.close()

thread = Thread(target=background_loop, daemon=True)

def start_background_loop():
    thread.start()

# Ensure the loop shuts down properly
def stop_background_loop():
    shutdown_event.set()
    loop.call_soon_threadsafe(loop.stop)

def run_async_in_background(coro_func, *args, **kwargs):
    """
    Run an async function in the background without awaiting it.
    Suitable for fire-and-forget tasks from synchronous code.
    """
    if not loop.is_running():
        raise RuntimeError("Background event loop is not running.")
    loop.call_soon_threadsafe(asyncio.create_task, coro_func(*args, **kwargs))
