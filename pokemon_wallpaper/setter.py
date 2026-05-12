import subprocess
from pathlib import Path


def set_gnome_wallpaper(image_path: Path) -> None:
    """Apply an image as the GNOME desktop wallpaper.

    Sets ``picture-uri``, ``picture-uri-dark``, and ``picture-options``
    via ``gsettings`` so the wallpaper is applied in both light and dark
    mode, scaled to fill the screen (zoom).

    Args:
        image_path: Absolute path to the image file to set as wallpaper.

    Raises:
        subprocess.CalledProcessError: If any ``gsettings`` call fails.
    """
    uri = image_path.resolve().as_uri()
    subprocess.run(
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri],
        check=True,
    )
    subprocess.run(
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri],
        check=True,
    )
    subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.background",
            "picture-options",
            "zoom",
        ],
        check=True,
    )
