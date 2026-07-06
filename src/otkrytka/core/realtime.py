"""In-memory pub/sub hub for live board updates over WebSockets.

Single-process uvicorn means a process-local registry is the correct fanout
mechanism: each board ``slug`` maps to the set of connected sockets. On any
mutation a route calls :meth:`BoardHub.publish` to push a lightweight
``{"type": "changed"}`` signal; clients react by refetching the board so new
cards appear for everyone watching.

No external dependencies — only Starlette/FastAPI's WebSocket and asyncio.
"""

import asyncio

from fastapi import WebSocket

_CHANGED: dict[str, str] = {"type": "changed"}
_HELLO: dict[str, str] = {"type": "hello"}


class BoardHub:
    """Process-local fanout of change signals, keyed by board slug."""

    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, slug: str, ws: WebSocket) -> None:
        """Accept the socket, register it under ``slug``, and greet the client."""
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(slug, set()).add(ws)
        await ws.send_json(_HELLO)

    async def disconnect(self, slug: str, ws: WebSocket) -> None:
        """Unregister a socket; drop the room when it becomes empty."""
        async with self._lock:
            room = self._rooms.get(slug)
            if room is None:
                return
            room.discard(ws)
            if not room:
                del self._rooms[slug]

    async def publish(self, slug: str) -> None:
        """Send ``{"type": "changed"}`` to every socket watching ``slug``.

        Dead/slow sockets that raise on send are pruned. Never raises — the
        mutation that triggered the publish has already committed.
        """
        async with self._lock:
            targets = list(self._rooms.get(slug, ()))
        if not targets:
            return

        # Fan out concurrently so one slow socket does not delay the others.
        results = await asyncio.gather(
            *(ws.send_json(_CHANGED) for ws in targets), return_exceptions=True
        )
        dead = [ws for ws, res in zip(targets, results) if isinstance(res, Exception)]

        if dead:
            async with self._lock:
                room = self._rooms.get(slug)
                if room is not None:
                    room.difference_update(dead)
                    if not room:
                        del self._rooms[slug]


# Module-level singleton shared across the app (single-process pub/sub).
hub = BoardHub()
