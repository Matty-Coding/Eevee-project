from datetime import datetime
from app.database.connection import Base
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Pokemon(Base):

    __tablename__ = "pokemon_name"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    pokedex_id: Mapped[str] = mapped_column(
        String(4), nullable=False
    )

    pokemon_details: Mapped[list["PokemonDetails"]] = relationship(
        "PokemonDetails", back_populates="pokemon_name", cascade="all, delete-orphan"
    )


class PokemonDetails(Base):

    __tablename__ = "pokemon_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pokemon_id: Mapped[int] = mapped_column(
        ForeignKey("pokemon_name.id"), nullable=False, index=True
    )

    # DETAILS
    owned: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    card_name: Mapped[str] = mapped_column(String(500), nullable=False)

    # SET / PRODUCT
    set_product: Mapped[str] = mapped_column(
        String(500), nullable=False, index=True)

    # CARD #
    card_number: Mapped[str] = mapped_column(String(10), nullable=True)

    # VARIANT / PRINTING
    variant_printing: Mapped[str] = mapped_column(
        String(500), nullable=False, index=True
    )

    # PRIMARY LANGUAGE
    representative_language: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    all_language: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    languages_count: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    # YES or NO
    same_card_other_language: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )

    other_languages: Mapped[str] = mapped_column(
        String(500), nullable=True
    )

    # RELEASED / PROTOTYPE / ANNOUNCED
    release_status: Mapped[str] = mapped_column(
        String(25), nullable=False, index=True
    )

    release_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )

    legacy_id: Mapped[str] = mapped_column(
        String(25), nullable=True
    )

    notes: Mapped[str] = mapped_column(
        String(500), nullable=True
    )

    card_image: Mapped[str] = mapped_column(
        String(500), nullable=False, default=r"https://www.affaridanerd.it/wp-content/uploads/2023/12/Pokemon-TCG-retro-carta.png"
    )

    pokemon_name: Mapped["Pokemon"] = relationship(
        "Pokemon", back_populates="pokemon_details"
    )
