import subprocess
import sys
from datetime import date
from importlib.metadata import version
from pathlib import Path

import click

from .pokemon import daily_id_sequence, fetch_pokemon
from .wallhaven import find_wallpaper, download_wallpaper, prune_wallpapers, WALLPAPER_DIR
from .setter import set_gnome_wallpaper
from .scheduler import install as _install, uninstall as _uninstall
from .state import (
    load_index,
    save_index,
    is_paused,
    set_paused,
    clear_paused,
    get_history_position,
    get_keep_images,
    set_keep_images,
)
from .history import (
    load as load_history,
    save as save_history,
    get_used_urls,
    append as append_history,
    update_last_path,
    get_today,
)


def _ensure_storage_preference() -> None:
    """Ask the user once how they want wallpapers stored, then persist the choice."""
    if get_keep_images() is not None:
        return

    import sys
    if not sys.stdin.isatty():
        # Non-interactive (e.g. systemd timer): default to keep all images.
        set_keep_images(True)
        return

    click.echo("")
    click.echo("First-time setup:")
    keep = click.confirm(
        "Save all wallpaper images locally?",
        default=True,
    )
    set_keep_images(keep)
    if not keep:
        click.echo("Entendido! Apenas as 3 wallpapers mais recentes serão mantidas no disco.\n")
    else:
        click.echo("Todas as wallpapers serão salvas localmente.\n")


@click.group(epilog="Author: Marcos Filipe Capella <https://github.com/capella-marcosfilipe>")
@click.version_option(version=version("pokemon-a-day-wallpaper"), prog_name="pokemon-wallpaper")
def main():
    """Daily Pokémon fan art wallpaper."""


def _apply_from_index(today: date, start_index: int, force_apply: bool = True) -> None:
    """Find, download, and set the next available wallpaper from today's sequence.

    Iterates over today's Pokémon sequence starting at ``start_index``,
    skipping Pokémon for which the PokéAPI fetch fails, Wallhaven returns no
    results, or whose wallpaper URL has already been used. Logs the applied
    wallpaper to history and saves the sequence index to state.

    Args:
        today: The current date.
        start_index: Position in today's sequence to start searching from.
        force_apply: If True, set the wallpaper on screen. If False, only
            fetch and log (used when the session is paused via 'previous').

    Raises:
        click.ClickException: If no new wallpaper is found from ``start_index``
            to the end of the sequence.
    """
    sequence = daily_id_sequence(today)
    used_urls = get_used_urls()

    for index in range(start_index, len(sequence)):
        pokemon_id = sequence[index]
        try:
            candidate = fetch_pokemon(pokemon_id)
        except Exception as e:
            click.echo(f"  Could not fetch #{pokemon_id}: {e}", err=True)
            continue

        click.echo(f"  Trying #{candidate['id']:03d} {candidate['name'].capitalize()}...")
        url = find_wallpaper(candidate["name"], today, excluded_urls=used_urls)
        if not url:
            continue

        types = ", ".join(t.capitalize() for t in candidate["types"])
        click.echo(f"  Found a wallpaper for {candidate['name'].capitalize()} ({types})!")

        click.echo("Downloading...")
        path = download_wallpaper(url, candidate["name"])

        append_history({
            "date": today.isoformat(),
            "pokemon": candidate["name"],
            "pokemon_id": candidate["id"],
            "types": candidate["types"],
            "url": url,
            "path": str(path),
        })
        save_index(today, index)

        if not get_keep_images():
            prune_wallpapers(keep=3)

        if force_apply:
            click.echo("Applying wallpaper...")
            set_gnome_wallpaper(path)
            click.echo(
                f"Done! Today's Pokémon: #{candidate['id']:03d} "
                f"{candidate['name'].capitalize()} ({types})."
            )
        else:
            click.echo(
                f"Logged for today: #{candidate['id']:03d} "
                f"{candidate['name'].capitalize()} ({types}). "
                f"Run 'refresh' to apply."
            )
        return

    raise click.ClickException("No more wallpapers found for today.")


def _apply_entry(entry: dict) -> Path:
    """Ensure the wallpaper file exists and return its path, re-downloading if needed."""
    path = Path(entry["path"])
    if not path.exists():
        click.echo(f"Re-downloading wallpaper for {entry['pokemon'].capitalize()}...")
        try:
            path = download_wallpaper(entry["url"], entry["pokemon"])
        except Exception as e:
            raise click.ClickException(f"Failed to re-download wallpaper: {e}")
        update_last_path(entry["url"], str(path))
    return path


@main.command()
def run():
    """Fetch and apply today's Pokémon wallpaper.

    If a wallpaper was already fetched today, re-applies it without making
    a new network request. If the session is paused (via 'previous'), the
    wallpaper is fetched and logged but not applied — use 'refresh' to resume.
    """
    _ensure_storage_preference()
    today = date.today()
    paused = is_paused()

    today_entry = get_today()
    if today_entry:
        if paused:
            click.echo("Today's wallpaper is already logged. Use 'refresh' to apply it.")
        else:
            path = _apply_entry(today_entry)
            click.echo("Applying today's wallpaper...")
            set_gnome_wallpaper(path)
            types = ", ".join(t.capitalize() for t in today_entry["types"])
            click.echo(
                f"Done! Today's Pokémon: #{today_entry['pokemon_id']:03d} "
                f"{today_entry['pokemon'].capitalize()} ({types})."
            )
        return

    click.echo("Selecting today's Pokémon...")
    _apply_from_index(today, start_index=0, force_apply=not paused)


@main.command()
def next():
    """Skip to the next Pokémon wallpaper for today."""
    _ensure_storage_preference()
    today = date.today()
    current_index = load_index(today)
    clear_paused()
    click.echo("Finding the next Pokémon...")
    _apply_from_index(today, start_index=current_index + 1, force_apply=True)


@main.command()
def previous():
    """Go back to the previous day's Pokémon wallpaper.

    Sets the session to paused mode. The wallpaper will not change
    automatically at midnight until you run 'refresh'.
    """
    _ensure_storage_preference()
    history = load_history()
    if len(history) < 2:
        raise click.ClickException("No previous wallpaper in history.")

    current_pos = get_history_position()
    new_pos = (len(history) - 2) if current_pos is None else (current_pos - 1)

    if new_pos < 0:
        raise click.ClickException("Already at the oldest wallpaper in history.")

    entry = history[new_pos]
    path = Path(entry["path"])

    if not path.exists():
        click.echo(f"Re-downloading wallpaper for {entry['pokemon'].capitalize()}...")
        try:
            path = download_wallpaper(entry["url"], entry["pokemon"])
        except Exception as e:
            raise click.ClickException(f"Failed to re-download wallpaper: {e}")
        entry["path"] = str(path)
        history[new_pos] = entry
        save_history(history)

    click.echo(f"Applying wallpaper from {entry['date']}...")
    set_gnome_wallpaper(path)
    set_paused(new_pos)

    types = ", ".join(t.capitalize() for t in entry["types"])
    click.echo(
        f"Showing: #{entry['pokemon_id']:03d} {entry['pokemon'].capitalize()} ({types}) "
        f"[{entry['date']}]. Run 'refresh' to return to today's wallpaper."
    )


@main.command()
def refresh():
    """Resume today's Pokémon wallpaper after using 'previous'.

    Clears the paused state and re-applies today's wallpaper. If today's
    wallpaper has not been fetched yet, it is fetched now.
    """
    _ensure_storage_preference()
    today = date.today()
    clear_paused()

    today_entry = get_today()
    if today_entry:
        path = Path(today_entry["path"])
        if not path.exists():
            click.echo("Re-downloading today's wallpaper...")
            try:
                path = download_wallpaper(today_entry["url"], today_entry["pokemon"])
            except Exception as e:
                raise click.ClickException(f"Failed to re-download wallpaper: {e}")
            update_last_path(today_entry["url"], str(path))
        click.echo("Applying today's wallpaper...")
        set_gnome_wallpaper(path)
        types = ", ".join(t.capitalize() for t in today_entry["types"])
        click.echo(
            f"Done! Today's Pokémon: #{today_entry['pokemon_id']:03d} "
            f"{today_entry['pokemon'].capitalize()} ({types})."
        )
    else:
        click.echo("No wallpaper for today yet. Fetching...")
        _apply_from_index(today, start_index=0, force_apply=True)


@main.command()
@click.option("--keep-images", "keep_images", is_flag=True, flag_value=True, default=None,
              help="Save all wallpaper images locally.")
@click.option("--no-keep-images", "keep_images", is_flag=True, flag_value=False,
              help="Keep only the 3 most recent wallpapers on disk.")
def config(keep_images):
    """Show or change configuration settings.

    Run without flags to see current settings.
    Use --keep-images / --no-keep-images to change the storage mode.
    """
    if keep_images is None:
        current = get_keep_images()
        if current is None:
            click.echo("Storage mode: not configured yet (will be asked on next run).")
        elif current:
            click.echo("Storage mode: keep all images (--keep-images).")
        else:
            click.echo("Storage mode: rolling cache — only 3 most recent kept (--no-keep-images).")
        return

    set_keep_images(keep_images)
    if keep_images:
        click.echo("Storage mode set: all wallpapers will be saved locally.")
    else:
        click.echo("Storage mode set: only the 3 most recent wallpapers will be kept on disk.")
        prune_wallpapers(keep=3)


@main.command()
def install():
    """Install the systemd timer and autostart entry for daily wallpaper updates.

    Sets up a systemd user timer that runs every day at 08:00 and an XDG
    autostart entry so the wallpaper is applied automatically when you log in.
    """
    try:
        _install()
        click.echo("Timer installed. Wallpaper will update daily at 08:00.")
        click.echo("Autostart enabled. Wallpaper will apply automatically on login.")
        click.echo("Run 'pokemon-wallpaper run' to apply today's wallpaper right now.")
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
def uninstall():
    """Remove the systemd timer and autostart entry."""
    try:
        _uninstall()
        click.echo("Timer and autostart removed.")
    except Exception as e:
        raise click.ClickException(str(e))


@main.command("list-wallpapers")
def list_wallpapers():
    """Show the wallpaper history."""
    history = load_history()
    if not history:
        click.echo("No wallpapers in history yet.")
        return

    for entry in reversed(history):
        types = ", ".join(t.capitalize() for t in entry["types"])
        path = Path(entry["path"])
        status = "ok" if path.exists() else "missing"
        click.echo(
            f"{entry['date']}  #{entry['pokemon_id']:03d} "
            f"{entry['pokemon'].capitalize():<12} ({types:<20})  [{status}]"
        )


@main.command("open-folder")
def open_folder():
    """Open the wallpaper folder in the file manager."""
    if not WALLPAPER_DIR.exists():
        raise click.ClickException(f"Folder does not exist yet: {WALLPAPER_DIR}")

    if sys.platform == "win32":
        subprocess.run(["explorer", str(WALLPAPER_DIR)], check=False)
    else:
        subprocess.run(["xdg-open", str(WALLPAPER_DIR)], check=False)

    click.echo(f"Opening {WALLPAPER_DIR}")
