import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "PokemonWallpaper"

SYSTEMD_USER_DIR = Path.home() / ".config" / "systemd" / "user"
AUTOSTART_DIR = Path.home() / ".config" / "autostart"
SERVICE_NAME = "pokemon-wallpaper.service"
TIMER_NAME = "pokemon-wallpaper.timer"
DESKTOP_NAME = "pokemon-wallpaper.desktop"
TASK_NAME = "PokemonWallpaper"

SERVICE_CONTENT = """\
[Unit]
Description=Daily Pokémon wallpaper

[Service]
Type=oneshot
ExecStart={exec_path} run
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/%U/bus
"""

TIMER_CONTENT = """\
[Unit]
Description=Daily Pokémon wallpaper timer

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""

DESKTOP_CONTENT = """\
[Desktop Entry]
Type=Application
Name=Pokémon Wallpaper
Comment=Apply today's Pokémon fan art wallpaper on login
Exec={exec_path} run
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""


def _install_linux() -> None:
    """Install the systemd user timer and XDG autostart entry.

    Writes unit files to ``~/.config/systemd/user/``, a ``.desktop`` file to
    ``~/.config/autostart/``, then enables and starts the timer so the
    wallpaper updates every day at 08:00 and is applied on each login.

    Raises:
        RuntimeError: If the ``pokemon-wallpaper`` executable is not found
            in ``PATH``.
        subprocess.CalledProcessError: If any ``systemctl`` call fails.
    """
    exec_path = shutil.which("pokemon-wallpaper")
    if exec_path is None:
        raise RuntimeError(
            "pokemon-wallpaper not found in PATH. "
            "Make sure the package is installed."
        )

    SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)

    (SYSTEMD_USER_DIR / SERVICE_NAME).write_text(
        SERVICE_CONTENT.format(exec_path=exec_path)
    )
    (SYSTEMD_USER_DIR / TIMER_NAME).write_text(TIMER_CONTENT)
    (AUTOSTART_DIR / DESKTOP_NAME).write_text(
        DESKTOP_CONTENT.format(exec_path=exec_path)
    )

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(
        ["systemctl", "--user", "enable", "--now", TIMER_NAME], check=True
    )


def _uninstall_linux() -> None:
    """Disable and remove the systemd timer and XDG autostart entry.

    Stops and disables ``pokemon-wallpaper.timer``, deletes the unit files
    from ``~/.config/systemd/user/``, removes the autostart ``.desktop``
    file, and reloads the systemd daemon. Failures are silently ignored so
    the function is safe to call even when nothing was installed.
    """
    subprocess.run(
        ["systemctl", "--user", "disable", "--now", TIMER_NAME],
        check=False,
    )

    for name in (SERVICE_NAME, TIMER_NAME):
        path = SYSTEMD_USER_DIR / name
        if path.exists():
            path.unlink()

    desktop = AUTOSTART_DIR / DESKTOP_NAME
    if desktop.exists():
        desktop.unlink()

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)


def _install_windows() -> None:
    exec_path = shutil.which("pokemon-wallpaper")
    if exec_path is None:
        raise RuntimeError(
            "pokemon-wallpaper not found in PATH. "
            "Make sure the package is installed."
        )

    # Daily run at 08:00
    subprocess.run(
        [
            "schtasks", "/create",
            "/tn", TASK_NAME,
            "/tr", f'"{exec_path}" run',
            "/sc", "daily",
            "/st", "08:00",
            "/f",
        ],
        check=True,
    )

    # Autostart on login via registry (no admin rights required)
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, RUN_VALUE_NAME, 0, winreg.REG_SZ, f'"{exec_path}" run')
    winreg.CloseKey(key)


def _uninstall_windows() -> None:
    subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"], check=False)

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, RUN_VALUE_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


def install() -> None:
    """Schedule the daily wallpaper update on the current platform.

    On Linux, installs a systemd user timer and an XDG autostart entry.
    On Windows, creates a daily Task Scheduler entry (08:00) and adds a
    registry Run key for login autostart (no admin rights required).

    Raises:
        RuntimeError: If the ``pokemon-wallpaper`` executable is not found
            in ``PATH``.
        subprocess.CalledProcessError: If the underlying scheduler call fails.
    """
    if sys.platform == "win32":
        _install_windows()
    else:
        _install_linux()


def uninstall() -> None:
    """Remove the daily wallpaper schedule on the current platform.

    On Linux, disables the systemd timer and removes the autostart entry.
    On Windows, deletes the Task Scheduler entry and the registry Run key.
    Failures are silently ignored so the function is safe to call even when
    nothing was installed.
    """
    if sys.platform == "win32":
        _uninstall_windows()
    else:
        _uninstall_linux()
