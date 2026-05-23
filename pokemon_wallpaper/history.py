import json
from datetime import date

from ._paths import DATA_DIR

HISTORY_FILE = DATA_DIR / "history.json"


def load() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, ValueError):
        return []


def save(history: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def get_used_urls() -> set[str]:
    return {entry["url"] for entry in load()}


def append(entry: dict) -> None:
    history = load()
    history.append(entry)
    save(history)


def update_last_path(url: str, new_path: str) -> None:
    history = load()
    for entry in reversed(history):
        if entry["url"] == url:
            entry["path"] = new_path
            save(history)
            return


def get_today() -> dict | None:
    today_str = date.today().isoformat()
    for entry in reversed(load()):
        if entry["date"] == today_str:
            return entry
    return None
