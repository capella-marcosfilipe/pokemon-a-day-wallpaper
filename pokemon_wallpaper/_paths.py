import os
import sys
from pathlib import Path

if sys.platform == "win32":
    DATA_DIR = (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
        / "pokemon-wallpaper"
    )
else:
    DATA_DIR = Path.home() / ".local" / "share" / "pokemon-wallpaper"
