from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from .schemas import PokemonResponse, PokemonUpdateRequest, PokemonDetailsResponse
from .services import get_all_pokemon, update_pokemon_record
from app.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/pokemon",
    tags=["Pokemon"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)]  # prefix locked by auth
)


@router.get("/", response_model=PokemonResponse, status_code=200)
async def get_pokemon(
    db: AsyncSession = Depends(get_db),
):
    return await get_all_pokemon(db)


@router.patch("/{details_id}", status_code=200, response_model=PokemonDetailsResponse)
async def update_pokemon(
    details_id: int,
    payload: PokemonUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_pokemon_record(db, details_id, payload)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
