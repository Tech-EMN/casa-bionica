"""Casa Biônica — RFC 9457 error handler (always shows detail for debugging)."""

import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def rfc9457_error_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None)

    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": f"https://httpstatuses.io/{exc.status_code}",
                "title": exc.detail or "HTTP Error",
                "status": exc.status_code,
                "instance": str(request.url),
                "trace_id": trace_id,
            },
        )

    # Always show detail + traceback for debugging
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://httpstatuses.io/500",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "traceback": traceback.format_exc()[-1000:],
            "instance": str(request.url),
            "trace_id": trace_id,
        },
    )
