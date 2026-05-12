import shutil
import subprocess
from pathlib import Path

SYSTEMD_USER_DIR = Path.home() / ".config" / "systemd" / "user"
SERVICE_NAME = "pokemon-wallpaper.service"
TIMER_NAME = "pokemon-wallpaper.timer"

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


def install() -> None:
    """Install the systemd user service and timer for daily wallpaper updates.

    Writes ``pokemon-wallpaper.service`` and ``pokemon-wallpaper.timer`` to
    ``~/.config/systemd/user/``, then enables and starts the timer so the
    wallpaper is updated every day at 08:00.

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

    (SYSTEMD_USER_DIR / SERVICE_NAME).write_text(
        SERVICE_CONTENT.format(exec_path=exec_path)
    )
    (SYSTEMD_USER_DIR / TIMER_NAME).write_text(TIMER_CONTENT)

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(
        ["systemctl", "--user", "enable", "--now", TIMER_NAME], check=True
    )


def uninstall() -> None:
    """Disable and remove the systemd user service and timer.

    Stops and disables ``pokemon-wallpaper.timer``, then deletes both unit
    files from ``~/.config/systemd/user/`` and reloads the systemd daemon.
    Failures during disable or reload are silently ignored so the function
    is safe to call even when the timer was never installed.
    """
    subprocess.run(
        ["systemctl", "--user", "disable", "--now", TIMER_NAME],
        check=False,
    )

    for name in (SERVICE_NAME, TIMER_NAME):
        path = SYSTEMD_USER_DIR / name
        if path.exists():
            path.unlink()

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
