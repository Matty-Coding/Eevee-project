from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# =========  PRODUCTION  ==========
# from sqlalchemy import URL
# DATABASE_URL = URL.create()

# database async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False  # avoid logging all statements
)

# async session
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    Allow to create tables as declarative models
    """
    pass


async def get_db():
    """
    Returns a database session
    """

    async with AsyncSessionLocal() as session:
        yield session  # generator to return the session
