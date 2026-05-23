import ctypes
import subprocess
import sys
from pathlib import Path

_SPI_SETDESKWALLPAPER = 0x0014
_SPIF_UPDATEINIFILE = 0x01
_SPIF_SENDCHANGE = 0x02


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


def set_windows_wallpaper(image_path: Path) -> None:
    """Apply an image as the Windows desktop wallpaper via SystemParametersInfo.

    Args:
        image_path: Absolute path to the image file to set as wallpaper.

    Raises:
        OSError: If the Windows API call fails.
    """
    path_str = str(image_path.resolve())
    ok = ctypes.windll.user32.SystemParametersInfoW(
        _SPI_SETDESKWALLPAPER, 0, path_str, _SPIF_UPDATEINIFILE | _SPIF_SENDCHANGE
    )
    if not ok:
        raise OSError("SystemParametersInfoW failed to set wallpaper")


def set_wallpaper(image_path: Path) -> None:
    """Apply an image as the desktop wallpaper on the current platform.

    Dispatches to :func:`set_windows_wallpaper` on Windows and
    :func:`set_gnome_wallpaper` on Linux/GNOME.

    Args:
        image_path: Absolute path to the image file to set as wallpaper.
    """
    if sys.platform == "win32":
        set_windows_wallpaper(image_path)
    else:
        set_gnome_wallpaper(image_path)
