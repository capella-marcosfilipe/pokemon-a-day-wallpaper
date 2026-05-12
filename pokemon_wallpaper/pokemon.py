import random
from datetime import date

import httpx

TOTAL_POKEMON = 1025
POKEAPI_BASE = "https://pokeapi.co/api/v2"


def daily_id_sequence(today: date | None = None) -> list[int]:
    """Returns a shuffled list of all Pokémon IDs seeded by today's date.

    The shuffle is deterministic per day: calling this function multiple times
    on the same date always returns the same order.

    Args:
        today: The reference date. Defaults to the current date.

    Returns:
        A list of all Pokémon IDs (1 to ``TOTAL_POKEMON``) in a
        date-seeded random order.
    """
    if today is None:
        today = date.today()
    ids = list(range(1, TOTAL_POKEMON + 1))
    random.Random(today.toordinal()).shuffle(ids)
    return ids


def fetch_pokemon(pokemon_id: int) -> dict:
    """Fetch basic data for a single Pokémon from the PokéAPI.

    Args:
        pokemon_id: The National Pokédex number of the Pokémon.

    Returns:
        A dict with keys ``id`` (int), ``name`` (str), and
        ``types`` (list[str]).

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status code.
        httpx.TimeoutException: If the request exceeds the timeout.
    """
    with httpx.Client(timeout=15) as client:
        resp = client.get(f"{POKEAPI_BASE}/pokemon/{pokemon_id}")
        resp.raise_for_status()
        data = resp.json()

    return {
        "id": data["id"],
        "name": data["name"],
        "types": [t["type"]["name"] for t in data["types"]],
    }
