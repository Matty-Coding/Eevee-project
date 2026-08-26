from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# =========  PRODUCTION  ==========
from sqlalchemy import URL
POSTGRES_DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DATABASE
)

# database async engine
engine = create_async_engine(
    POSTGRES_DATABASE_URL if settings.PRODUCTION else settings.DATABASE_URL,
    echo=False,  # avoid logging all statements
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
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
