from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.auth.services import get_user_by_id
from app.auth.utils import check_access_token

security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):

    payload = check_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = await get_user_by_id(db, int(payload["sub"]))

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    return db_user
