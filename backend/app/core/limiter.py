from slowapi import Limiter
from fastapi.responses import JSONResponse
from slowapi.util import get_remote_address
from datetime import datetime, timezone
import time


from pydantic import BaseModel


class RateLimitError(BaseModel):
    error: str
    unlock_at: datetime


limiter = Limiter(key_func=get_remote_address)


async def custom_rate_limit_handler(request, exc):
    """
    Custom rate limit handler returns 429 status code with reset time
    """

    limit_item, key_parts = request.state.view_rate_limit

    # reset timer + remaining attempts as a tuple
    reset_time, _ = request.app.state.limiter.limiter.get_window_stats(
        limit_item, *key_parts)

    # convert timestamp to datetime
    unlock_at = datetime.fromtimestamp(reset_time, tz=timezone.utc)

    payload = RateLimitError(
        error="Too many requests. Try again later.",
        unlock_at=unlock_at
    )

    return JSONResponse(
        status_code=429,
        content=payload.model_dump(mode="json"),
        headers={
            # str of max value (0 or any int value)
            # handling negative values from response
            "Retry-After": str(max(0, int(reset_time - time.time())))
        }
    )
