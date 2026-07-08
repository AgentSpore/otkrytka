"""Pure-ASGI request-body size limit.

Two caps: a large one for the image-upload path and a small default for every
other HTTP route (JSON APIs never need a big body). Starlette's ``MultiPartParser``
spools file parts to a temp file with NO size check (``max_part_size`` is a no-op
for file parts), and a plain JSON route reads the whole body into memory, so both
are unbounded-read DoS surfaces without this.

A Content-Length check alone is bypassable by a chunked / length-less body, so
this middleware ALSO caps the streamed bytes: it wraps ``receive`` and aborts with
413 the moment the accumulated body exceeds the cap, before the body is spooled or
buffered further.
"""

from loguru import logger
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_UPLOAD_PREFIX = "/api/v1/boards/"
_UPLOAD_SUFFIX = "/upload"
# Small allowance for multipart boundaries / part headers on top of the raw
# image cap, so a valid at-cap image is not rejected for its envelope overhead.
_MULTIPART_OVERHEAD = 16 * 1024
# Default cap for every non-upload HTTP route: JSON bodies here are tiny (a title,
# a wish, a token), so 64 KB is generous while closing the DoS surface.
_DEFAULT_MAX_BYTES = 64 * 1024

_UPLOAD_TOO_LARGE = b'{"detail":{"code":"image_too_large","message":"Image is too large"}}'
_BODY_TOO_LARGE = b'{"detail":{"code":"request_too_large","message":"Request body too large"}}'


class _BodyTooLarge(Exception):
    """Raised from the wrapped ``receive`` once the streamed body exceeds the cap."""


class BodySizeLimitMiddleware:
    """Reject an oversized request body at the ASGI layer (413) before it is read."""

    def __init__(
        self,
        app: ASGIApp,
        max_upload_bytes: int,
        default_max_bytes: int = _DEFAULT_MAX_BYTES,
    ) -> None:
        self.app = app
        self.upload_max = max_upload_bytes + _MULTIPART_OVERHEAD
        self.default_max = default_max_bytes

    def _is_upload(self, scope: Scope) -> bool:
        path = scope.get("path", "")
        return (
            scope.get("method") == "POST"
            and path.startswith(_UPLOAD_PREFIX)
            and path.endswith(_UPLOAD_SUFFIX)
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # websocket / lifespan carry no request body
            await self.app(scope, receive, send)
            return

        upload = self._is_upload(scope)
        max_bytes = self.upload_max if upload else self.default_max
        reject_body = _UPLOAD_TOO_LARGE if upload else _BODY_TOO_LARGE

        # Fast path: a declared Content-Length over the cap is rejected outright.
        for name, value in scope.get("headers", ()):
            if name == b"content-length":
                try:
                    declared = int(value)
                except ValueError:
                    # Malformed Content-Length: ignore it and let the streaming
                    # byte cap below do the enforcement instead.
                    break
                if declared > max_bytes:
                    await self._reject(send, reject_body)
                    return
                break

        received = 0

        async def capped_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > max_bytes:
                    raise _BodyTooLarge()
            return message

        started = False

        async def guarded_send(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, capped_receive, guarded_send)
        except _BodyTooLarge:
            logger.warning("Request body exceeded {} bytes on {}", max_bytes, scope.get("path"))
            if not started:
                await self._reject(send, reject_body)

    async def _reject(self, send: Send, body: bytes) -> None:
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        })
        await send({"type": "http.response.body", "body": body})
