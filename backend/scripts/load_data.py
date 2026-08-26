import asyncio
from app.database.connection import get_db
from .utils import find_image_url
from csv import DictReader
import requests
from bs4 import BeautifulSoup
from app.pokemon.models import Pokemon, PokemonDetails
from datetime import datetime


def generate_pokemon_json():
    BASE_URL = "https://www.tcgcollector.com/pokedex/133/eevee?releaseDateOrder=oldToNew&displayAs=images&pokemonCardCountMode=anyCardVariant"

    response = requests.get(BASE_URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        cards = soup.select(".card-image-grid-item-link")

        eevee_details = []
        for card in cards:
            title = card.get("title")

            # image url
            img_tag = card.select_one(".card-image-grid-item-image")
            image_url = img_tag.get("src")

            eevee_details.append({
                "title": title,
                "image_url": image_url
            })

        # with open("pokemon.json", "w", encoding="utf-8") as file:
        #     json.dump(eevee_details, file, indent=4, ensure_ascii=False)

        return eevee_details


async def insert_into_db():
    pokemon_object = Pokemon(
        name="eevee",
        pokedex_id="0133"
    )

    async for db in get_db():
        db.add(pokemon_object)
        await db.flush()

        file_path = r"C:\Users\matty\Desktop\hellkiche\backend\data\eevee_global_unique_master_tracker.csv"

        pokemon_details_list = []

        with open(file_path, "r", encoding="latin1") as file:
            content = DictReader(file, delimiter=";")

            for row in content:
                card_name, set_product, card_number, variant_printing = row["Unique Version Key"].split(
                    " | ")

                pokemon_details_object = PokemonDetails(
                    pokemon_id=pokemon_object.id,
                    owned=row.get("Owned").strip().lower() == "yes",
                    quantity=row.get("Qty").strip(),
                    card_name=card_name.strip() if not card_name.strip() == "Eevee ?" else "Eevee \u03b4",
                    set_product=set_product.strip(),
                    card_number=card_number.strip(),
                    variant_printing=variant_printing.strip(),
                    representative_language=row.get(
                        "Representative Language").strip(),
                    all_language=row.get(
                        "All Languages (same card/version)").strip(),
                    languages_count=row.get("Language Count").strip(),
                    same_card_other_language=row.get(
                        "Same card in other languages?"
                    ).strip().lower() == "yes",
                    other_languages=row.get("Other Languages", "").strip(),
                    release_status=row.get("Release Status").strip(),
                    release_date=(
                        datetime.strptime(
                            row.get("Release Date").strip(), "%Y-%m-%d").date()
                    ),  # giorno - mese - anno
                    legacy_id=row.get("Legacy ID", "").strip(),
                    notes=row.get("Notes", "").strip(),
                    card_image=find_image_url(
                        card_name.strip(),
                        set_product.strip(),
                        card_number.strip(),
                        variant_printing.strip(),
                    )
                )

                pokemon_details_list.append(pokemon_details_object)

        db.add_all(pokemon_details_list)
        await db.commit()

        break


if __name__ == "__main__":
    print("Inizio l'inserimento nel database...")

    # asyncio.run() crea un event loop, esegue la tua funzione asincrona e poi si chiude
    asyncio.run(insert_into_db())

    print("Finito!")
