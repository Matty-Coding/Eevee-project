import bcrypt
from datetime import datetime, timezone, timedelta
from jose import jwt
from app.core.config import settings
from itsdangerous import URLSafeTimedSerializer
from fastapi import Response


def generate_hashed_password(password: str) -> str:
    """
    Returns hashed password
    """

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def check_hashed_password(password: str, hashed: str) -> bool:
    """
    Checks if password is correct
    """

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


def generate_access_token(data: dict) -> str:
    """
    Returns access token
    """

    expire = (
        datetime.now(timezone.utc) +
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    )
    return jwt.encode(
        {**data, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def check_access_token(token: str) -> dict | None:
    """
    Decodes access token and returns payload
    """

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except Exception:
        return None


def generate_refresh_token(data: dict, csrf_token: str) -> str:
    """
    Returns refresh token including csrf token in payload
    """

    expire = (
        datetime.now(timezone.utc) +
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE)
    )
    return jwt.encode(
        {**data, "exp": expire, "csrf_token": csrf_token},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def check_refresh_token(token: str) -> dict | None:
    """
    Decodes refresh token and returns payload
    """

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except Exception:
        return None

# ====================================
# =============  CSRF  ===============
# ====================================


def generate_csrf_token(user_id: str) -> str:
    serializer = URLSafeTimedSerializer(settings.CSRF_SECRET_KEY)
    return serializer.dumps(user_id, salt="csrf")


def check_csrf_token(token: str) -> str | None:
    serializer = URLSafeTimedSerializer(settings.CSRF_SECRET_KEY)
    try:
        # during as long as refresh token is valid
        # matching the expiration of the refresh token
        max_age_seconds = 60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE
        return serializer.loads(token, salt="csrf", max_age=max_age_seconds)
    except Exception:
        return None


def set_tokens(response: Response, refresh_token: str, csrf_token: str) -> None:
    """
    Sets refresh token in cookie and csrf token in header of response
    """

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="none" if settings.PRODUCTION else "lax",   # cross-site cookie
        secure=True if settings.PRODUCTION else False,       # https only
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE
    )

    response.headers["X-CSRF-Token"] = csrf_token
