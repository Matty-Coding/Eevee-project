from app.database.connection import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .utils import (
    generate_hashed_password,
    check_hashed_password,
    generate_access_token,
    check_access_token,
    generate_refresh_token,
    check_refresh_token,
    generate_csrf_token,
    check_csrf_token
)
from .schemas import LoginRequest


async def add_user(username: str, password: str) -> None:
    async with AsyncSessionLocal() as session:
        user = User(
            username=username,
            hashed_password=generate_hashed_password(password)
        )
        session.add(user)
        await session.commit()


async def get_user_by_id(db: AsyncSession, id: int) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.id == id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.username == username)
    )
    return result.scalar_one_or_none()


def _generate_login_tokens(user_id: int) -> dict:
    csrf_token = generate_csrf_token(user_id)

    token_data = {"sub": str(user_id)}

    access_token = generate_access_token({"sub": str(user_id)})
    refresh_token = generate_refresh_token(token_data, csrf_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "csrf_token": csrf_token
    }


async def login_user(db: AsyncSession, payload: LoginRequest) -> dict | None:

    db_user = await get_user_by_username(db, payload.username)

    if not db_user or not check_hashed_password(payload.password, db_user.hashed_password):
        raise ValueError("Invalid credentials")

    tokens = _generate_login_tokens(db_user.id)

    return {
        "username": db_user.username,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "csrf_token": tokens["csrf_token"]
    }


async def refresh_auth_token(db: AsyncSession, refresh_token: str) -> dict | None:

    refresh_token_data = check_refresh_token(refresh_token)

    if not refresh_token_data:
        raise ValueError("Invalid refresh token")

    db_user = await get_user_by_id(db, int(refresh_token_data["sub"]))

    if not db_user:
        raise ValueError("User not found")

    tokens = _generate_login_tokens(db_user.id)

    return {
        "username": db_user.username,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "csrf_token": tokens["csrf_token"]
    }
