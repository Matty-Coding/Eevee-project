from fastapi.security import HTTPBearer
from app.core.config import settings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base
from app.core.limiter import custom_rate_limit_handler, limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth.routes import router as auth_router
from app.pokemon.routes import router as pokemon_router


# @asynccontextmanager
# async def lifespan(app: FastAPI):

#     # Initialize tables on supabase if doesn't exist
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield

#     # Close the connection
#     await engine.dispose()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            # Stampa le tabelle rilevate prima di crearle
            print(
                f"Tabelle registrate in metadata: {list(Base.metadata.tables.keys())}")
            print(f"DEBUG DB CONNECTED TO: {engine.url.host} / DB: {engine.url.database}")
            await conn.run_sync(Base.metadata.create_all)
            print("Tabelle create con successo su Supabase.")
    except Exception as e:
        print(f"Errore durante la creazione delle tabelle: {e}")

    yield

    await engine.dispose()

# auth token in Dependencies
security = HTTPBearer()

app = FastAPI(
    # for supabase register
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan  # for supabase register life cycle
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"],
)

# throttle limit
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)


# Routes
app.include_router(auth_router)
app.include_router(pokemon_router)
