import json
from datetime import date

from ._paths import DATA_DIR

STATE_FILE = DATA_DIR / "state.json"


def _read() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, ValueError):
        return {}


def _write(data: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data))


def load_index(today: date) -> int:
    data = _read()
    if data.get("date") == today.isoformat():
        return int(data.get("index", 0))
    return 0


def save_index(today: date, index: int) -> None:
    data = _read()
    data["date"] = today.isoformat()
    data["index"] = index
    _write(data)


def is_paused() -> bool:
    return _read().get("paused", False)


def get_history_position() -> int | None:
    return _read().get("history_position", None)


def set_paused(position: int) -> None:
    data = _read()
    data["paused"] = True
    data["history_position"] = position
    _write(data)


def clear_paused() -> None:
    data = _read()
    data["paused"] = False
    data["history_position"] = None
    _write(data)
