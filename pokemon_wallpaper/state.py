import json
from datetime import date
from pathlib import Path

STATE_FILE = Path.home() / ".local" / "share" / "pokemon-wallpaper" / "state.json"


def load(today: date) -> int:
    """Return the current sequence index for today.

    Reads the state file and returns the saved index if the stored date
    matches ``today``. Returns 0 if the file does not exist, is malformed,
    or belongs to a different date.

    Args:
        today: The current date, used to validate the stored state.

    Returns:
        The index of the last applied Pokémon in today's sequence, or 0
        if no valid state exists for today.
    """
    if not STATE_FILE.exists():
        return 0
    try:
        data = json.loads(STATE_FILE.read_text())
        if data.get("date") == today.isoformat():
            return int(data.get("index", 0))
    except (json.JSONDecodeError, ValueError):
        pass
    return 0


def save(today: date, index: int) -> None:
    """Persist the current sequence index for today.

    Creates the parent directory if it does not exist, then writes
    ``{"date": "<iso-date>", "index": <index>}`` to the state file,
    overwriting any previous state.

    Args:
        today: The current date, stored alongside the index.
        index: The index of the Pokémon just applied in today's sequence.
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"date": today.isoformat(), "index": index}))
