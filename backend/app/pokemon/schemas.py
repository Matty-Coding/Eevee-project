from pydantic import BaseModel, field_serializer
from datetime import datetime


class PokemonDetailsResponse(BaseModel):
    id: int
    owned: bool
    quantity: int
    card_name: str
    set_product: str
    card_number: str | None
    variant_printing: str
    representative_language: str
    all_language: str
    languages_count: int
    same_card_other_language: bool
    other_languages: str | None
    release_status: str
    release_date: datetime
    legacy_id: str | None
    notes: str | None
    card_image: str

    @field_serializer("release_date")
    def serialize_release_date(self, value: datetime) -> str:
        return value.strftime("%d-%m-%Y")  # giorno - mese - anno


class PokemonUpdateRequest(BaseModel):
    owned: bool | None = None
    quantity: int | None = None
    card_image: str | None = None


class PokemonResponse(BaseModel):
    name: str
    pokedex_id: str
    pokemon_details: list[PokemonDetailsResponse]
