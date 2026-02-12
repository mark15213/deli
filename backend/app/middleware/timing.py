import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware.timing")

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        process_time_ms = int(process_time * 1000)
        
        # Log the details
        # Format: Method Path Status Duration
        logger.info(
            f"{request.method} {request.url.path} "
            f"Status:{response.status_code} "
            f"Duration:{process_time_ms}ms"
        )
        
        # Optional: Add header to response so client can see it too
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
