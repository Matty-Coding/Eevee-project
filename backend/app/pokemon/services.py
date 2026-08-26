from .models import PokemonDetails, Pokemon
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import PokemonDetailsResponse, PokemonResponse, PokemonUpdateRequest


async def _get_pokemon_details(db: AsyncSession, id: int) -> PokemonDetailsResponse | None:
    result = await db.execute(
        select(PokemonDetails)
        .where(PokemonDetails.id == id)
    )
    return result.scalar_one_or_none()


async def get_all_pokemon(db: AsyncSession) -> PokemonResponse:
    result = await db.execute(
        select(Pokemon)
        .options(selectinload(Pokemon.pokemon_details))
    )
    data = result.scalars().all()

    return PokemonResponse(
        name=data[0].name,
        pokedex_id=data[0].pokedex_id,
        pokemon_details=[
            PokemonDetailsResponse(**detail.__dict__)
            for detail in data[0].pokemon_details
        ]
    )


async def update_pokemon_record(db: AsyncSession, id: int, payload: PokemonUpdateRequest) -> PokemonDetailsResponse:
    record = await _get_pokemon_details(db, id)

    if not record:
        raise ValueError("Record not found")

    record.owned = payload.owned if payload.owned is not None else record.owned
    record.quantity = payload.quantity if payload.quantity is not None else record.quantity
    record.card_image = payload.card_image if payload.card_image is not None else record.card_image

    await db.commit()
    await db.refresh(record)

    return PokemonDetailsResponse(**record.__dict__)
