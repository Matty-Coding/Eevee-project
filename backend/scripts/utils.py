import re
import unicodedata
from functools import lru_cache
import json


def read_json():
    with open(r"C:\Users\matty\Desktop\hellkiche\backend\data\pokemon.json", "r", encoding="utf-8") as file:
        return json.load(file)


def _normalize_text(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


# Nomi differenti usati dal CSV e da TCGCollector.
_SET_ALIASES = {
    "rocket gang": "team rocket",
    "vending machine expansion sheet 1 blue":
        "vending machine series 1 blue",
    "wizards promos": "wizards of the coast promos",
    "unnumbered promos": "miscellaneous promos",
    "pokemon card game battle academy": "battle academy",
    "151": "card 151",
    "pcg p promos": "pcg promos",
}


def _normalize_set(value):
    value = _normalize_text(value)
    value = _SET_ALIASES.get(value, value)

    # Rimuove prefissi non significativi.
    value = re.sub(r"^pokemon card game ", "", value)
    value = re.sub(r"^pokemon ", "", value)

    return _SET_ALIASES.get(value, value)


def _normalize_number(value):
    value = str(value or "").strip()

    if _normalize_text(value) in {
        "unnumbered",
        "no number",
        "none",
    }:
        return None

    value = re.sub(
        r"^no\.\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = value.upper().replace(" ", "")

    # 045/066 e 45/66 vengono considerati equivalenti.
    normalized_parts = []

    for part in value.split("/"):
        match = re.fullmatch(
            r"([^0-9]*)([0-9]+)([^0-9]*)",
            part,
        )

        if match:
            part = (
                f"{match.group(1)}"
                f"{int(match.group(2))}"
                f"{match.group(3)}"
            )

        normalized_parts.append(part)

    return "/".join(normalized_parts)


_TITLE_RE = re.compile(
    r"^\s*(?P<name>.+?)\s+\((?P<body>.+)\)\s*$"
)

_NUMBER_AT_END_RE = re.compile(
    r"^(?P<set>.+?)\s+"
    r"(?P<number>"
    r"(?:No\.\s*)?"
    r"[A-Z0-9#-]*\d[A-Z0-9#-]*"
    r"(?:/[A-Z0-9#-]+)?"
    r")$",
    re.IGNORECASE,
)


def _parse_title(title):
    """
    Esempio:
    'Eevee (Jungle 51/64)'
        -> ('Eevee', 'Jungle', '51/64', False)

    'Eevee (Pokémon Jungle No. 037)'
        -> ('Eevee', 'Pokémon Jungle', '37', True)
    """
    title_match = _TITLE_RE.fullmatch(title or "")

    if not title_match:
        return None

    number_match = _NUMBER_AT_END_RE.fullmatch(
        title_match.group("body")
    )

    if not number_match:
        return None

    raw_number = number_match.group("number")

    return (
        title_match.group("name"),
        number_match.group("set"),
        _normalize_number(raw_number),
        bool(
            re.match(
                r"^No\.",
                raw_number,
                flags=re.IGNORECASE,
            )
        ),
    )


@lru_cache(maxsize=1)
def _pokemon_cards():
    # Evita di rileggere pokemon.json per ogni riga del CSV.
    return tuple(read_json())


def find_image_url(
    card_name,
    set_product,
    card_number,
    variant_printing,
):
    """
    Restituisce l'URL esatto dell'immagine oppure None.

    Restituisce None anche quando più record JSON compatibili
    hanno URL diversi e la variante non permette di distinguerli.
    """
    wanted_name = _normalize_text(card_name)
    wanted_set = _normalize_set(set_product)
    wanted_number = _normalize_number(card_number)
    wanted_variant = _normalize_text(variant_printing)

    matches = []

    for card in _pokemon_cards():
        parsed = _parse_title(card.get("title", ""))

        if parsed is None:
            continue

        (
            json_name,
            json_set,
            json_number,
            json_uses_no_prefix,
        ) = parsed

        if _normalize_text(json_name) != wanted_name:
            continue

        if _normalize_set(json_set) != wanted_set:
            continue

        if wanted_number is None:
            # Nel JSON le carte giapponesi "Unnumbered"
            # sono indicate come "No. 037", "No. 049", ecc.
            if not json_uses_no_prefix:
                continue
        elif json_number != wanted_number:
            continue

        image_url = card.get("image_url")

        if not image_url:
            continue

        # Non restituisce l'immagine segnaposto.
        if "default-card-image" in image_url:
            continue

        matches.append(card)

    if not matches:
        return None

    # La variante viene usata come criterio aggiuntivo solo
    # quando è effettivamente presente nel title JSON.
    if wanted_variant:
        variant_matches = [
            card
            for card in matches
            if wanted_variant
            in _normalize_text(card.get("title", ""))
        ]

        if variant_matches:
            matches = variant_matches

    unique_urls = list(
        dict.fromkeys(card["image_url"] for card in matches)
    )

    # Nessuna scelta arbitraria quando gli URL sono diversi.
    if len(unique_urls) != 1:
        return None

    return unique_urls[0]
