"""
Shared Server-Sent Events helper for long-running Gemma endpoints.

The Next.js dev proxy (Turbopack) drops idle sockets at ~30s. A plain
non-streaming handler that waits 40-75 seconds for a Gemma function-calling
or thinking-mode call is invisible to the browser even though the backend
returns 200. The fix is to keep the socket warm with periodic heartbeat
frames while the real work runs in a background thread.

Usage::

    async def event_source():
        async for frame in run_streaming_job(
            lambda: progress_analyst.analyze(student_id, goal_id),
            heartbeat_interval=4.0,
        ):
            yield frame

    return StreamingResponse(event_source(), media_type="text/event-stream")

Protocol frames (one SSE frame per ``yield``):
  - ``data: {"status": "working", "message": "..."}\\n\\n`` — heartbeat
  - ``data: {"result": <payload>}\\n\\n`` — final success payload
  - ``data: {"error": "..."}\\n\\n`` — terminal error
  - ``data: {"done": true}\\n\\n`` — always the last frame
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Awaitable, Callable

logger = logging.getLogger(__name__)

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


def sse_frame(payload: dict[str, Any]) -> str:
    """Serialize a dict to an SSE data frame."""
    return f"data: {json.dumps(payload)}\n\n"


async def run_streaming_job(
    job: Callable[[], Any] | Callable[[], Awaitable[Any]],
    *,
    heartbeat_interval: float = 4.0,
    heartbeat_message: str = "Thinking…",
) -> AsyncIterator[str]:
    """Run a blocking (or async) job with SSE heartbeat frames.

    While the job is running, emit a ``status: working`` frame every
    ``heartbeat_interval`` seconds so proxies see activity on the socket.
    When the job finishes, emit the final ``result`` (or ``error``) frame
    followed by a ``done`` frame.

    The job runs in a worker thread via ``asyncio.to_thread`` so synchronous
    provider calls (Google AI Studio blocking HTTP requests) don't starve
    the event loop.
    """

    async def _runner() -> Any:
        result = job()
        if asyncio.iscoroutine(result):
            return await result
        # Offload sync work so heartbeats keep firing.
        return await asyncio.to_thread(lambda: result if not callable(result) else result())

    # Start the work.
    if asyncio.iscoroutinefunction(job):
        task = asyncio.create_task(job())  # type: ignore[arg-type]
    else:
        task = asyncio.create_task(asyncio.to_thread(job))

    # Immediate heartbeat so the browser sees the stream open.
    yield sse_frame({"status": "working", "message": heartbeat_message})

    try:
        while not task.done():
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=heartbeat_interval)
            except asyncio.TimeoutError:
                yield sse_frame({"status": "working", "message": heartbeat_message})
                continue
            break

        result = task.result()
        yield sse_frame({"result": result})
    except Exception as exc:  # noqa: BLE001 — surface any failure to the client
        logger.exception("SSE job failed: %s", exc)
        yield sse_frame({"error": str(exc)})
    finally:
        yield sse_frame({"done": True})
