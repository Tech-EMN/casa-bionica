"""Casa Biônica — RFC 9457 error handler middleware."""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def rfc9457_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Formata erros no padrão RFC 9457 (Problem Details)."""
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

    # Unhandled error
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://httpstatuses.io/500",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc) if request.app.debug else None,
            "instance": str(request.url),
            "trace_id": trace_id,
        },
    )
