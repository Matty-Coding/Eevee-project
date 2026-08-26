from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from app.core.limiter import limiter
from .schemas import LoginRequest, LoginResponse
from app.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .services import login_user, refresh_auth_token
from .utils import set_tokens


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=LoginResponse, status_code=200)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await login_user(db, payload)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    set_tokens(response, data["refresh_token"], data["csrf_token"])

    return LoginResponse(
        username=data["username"],
        access_token=data["access_token"],
    )


@router.post("/refresh-token", response_model=LoginResponse, status_code=200)
async def refresh_token(
    response: Response,
    # permette di accedere al cookie refresh_token
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await refresh_auth_token(db, refresh_token)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    set_tokens(response, data["refresh_token"], data["csrf_token"])

    return LoginResponse(
        username=data["username"],
        access_token=data["access_token"],
    )


@router.post("/logout", status_code=200)
async def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return {"message": "Logout successful"}
