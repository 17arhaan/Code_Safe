"""Asynchronous utility functions."""
import asyncio
from typing import List, Callable, Any

async def run_concurrent(tasks: List[Callable]) -> List[Any]:
    """Run multiple tasks concurrently."""
    return await asyncio.gather(*tasks)

async def run_with_timeout(coro, timeout: float) -> Any:
    """Run coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")

async def delay(seconds: float) -> None:
    """Delay execution for specified seconds."""
    await asyncio.sleep(seconds)
