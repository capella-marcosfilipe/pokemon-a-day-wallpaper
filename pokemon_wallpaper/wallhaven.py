import random
from datetime import date
from pathlib import Path

import httpx

from ._paths import DATA_DIR

WALLHAVEN_SEARCH = "https://wallhaven.cc/api/v1/search"
WALLPAPER_DIR = Path.home() / ".local" / "share" / "pokemon-wallpaper"
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def find_wallpaper(
    pokemon_name: str,
    today: date | None = None,
    excluded_urls: set[str] | None = None,
) -> str | None:
    """Search Wallhaven for a fan art wallpaper of the given Pokémon.

    Queries the Wallhaven API for SFW anime wallpapers at 1920x1080 or
    higher, sorted by number of favorites. The choice among the results is
    deterministic per (Pokémon, date) pair, skipping any URLs already in
    ``excluded_urls`` so the same wallpaper is never shown twice.

    Args:
        pokemon_name: The Pokémon's name as returned by the PokéAPI
            (e.g. ``"pikachu"``).
        today: The reference date used to seed the result selection.
            Defaults to the current date.
        excluded_urls: Set of wallpaper URLs already used; matched results
            are skipped. Pass ``None`` to disable deduplication.

    Returns:
        The direct URL of the chosen wallpaper, or ``None`` if no unseen
        results were found for this Pokémon.

    Raises:
        httpx.HTTPStatusError: If the Wallhaven API returns a non-2xx status.
        httpx.TimeoutException: If the request exceeds the timeout.
    """
    params = {
        "q": f"{pokemon_name} pokemon",
        "atleast": "1920x1080",
        "categories": "010",  # anime
        "purity": "100",      # SFW only
        "sorting": "favorites",
        "order": "desc",
    }

    with httpx.Client(timeout=15) as client:
        resp = client.get(WALLHAVEN_SEARCH, params=params)
        resp.raise_for_status()
        results = resp.json().get("data", [])

    if not results:
        return None

    if excluded_urls:
        results = [r for r in results if r["path"] not in excluded_urls]
        if not results:
            return None

    if today is None:
        today = date.today()

    rng = random.Random(today.toordinal() + hash(pokemon_name))
    chosen = rng.choice(results)
    return chosen["path"]


def download_wallpaper(url: str, pokemon_name: str) -> Path:
    """Download a wallpaper image to the local cache directory.

    The file is saved as ``<WALLPAPER_DIR>/{name}.{ext}``, overwriting any
    previously downloaded wallpaper for the same Pokémon.

    Args:
        url: Direct URL of the wallpaper image.
        pokemon_name: The Pokémon's name, used as the filename stem.

    Returns:
        The ``Path`` of the downloaded file.

    Raises:
        httpx.HTTPStatusError: If the download request returns a non-2xx status.
        httpx.TimeoutException: If the download exceeds the timeout.
    """
    WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

    suffix = url.rsplit(".", 1)[-1]
    dest = WALLPAPER_DIR / f"{pokemon_name}.{suffix}"

    with httpx.Client(timeout=60, follow_redirects=True) as client:
        with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_bytes(chunk_size=8192):
                    f.write(chunk)

    return dest


def prune_wallpapers(keep: int = 3) -> None:
    """Delete local wallpaper files beyond the ``keep`` most recent ones.

    Reads history to determine which files are still relevant, then removes
    any image file in WALLPAPER_DIR that is not among the ``keep`` most
    recently referenced paths.
    """
    from .history import load as load_history

    history = load_history()
    recent_paths: list[Path] = []
    for entry in reversed(history):
        p = entry.get("path", "")
        if p:
            candidate = Path(p)
            if candidate not in recent_paths:
                recent_paths.append(candidate)
        if len(recent_paths) >= keep:
            break

    keep_set = set(recent_paths)

    if not WALLPAPER_DIR.exists():
        return

    for f in WALLPAPER_DIR.iterdir():
        if f.suffix.lower() in _IMAGE_SUFFIXES and f not in keep_set:
            f.unlink(missing_ok=True)
