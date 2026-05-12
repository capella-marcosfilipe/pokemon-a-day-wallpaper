from datetime import date

import click

from .pokemon import daily_id_sequence, fetch_pokemon
from .wallhaven import find_wallpaper, download_wallpaper
from .setter import set_gnome_wallpaper
from .scheduler import install as _install, uninstall as _uninstall
from .state import load as load_state, save as save_state


@click.group()
def main():
    """Daily Pokémon fan art wallpaper for Ubuntu GNOME."""


def _apply_from_index(today: date, start_index: int) -> None:
    """Find, download, and apply the next available wallpaper from the sequence.

    Iterates over today's Pokémon sequence starting at ``start_index``,
    skipping any Pokémon for which the PokéAPI fetch fails or Wallhaven
    returns no results. Saves the applied index to the state file.

    Args:
        today: The current date, used to build the sequence and persist state.
        start_index: The position in today's sequence to start searching from.

    Raises:
        click.ClickException: If no wallpaper is found from ``start_index``
            to the end of the sequence.
    """
    sequence = daily_id_sequence(today)

    for index in range(start_index, len(sequence)):
        pokemon_id = sequence[index]
        try:
            candidate = fetch_pokemon(pokemon_id)
        except Exception as e:
            click.echo(f"  Could not fetch #{pokemon_id}: {e}", err=True)
            continue

        click.echo(f"  Trying #{candidate['id']:03d} {candidate['name'].capitalize()}...")
        url = find_wallpaper(candidate["name"], today)
        if not url:
            continue

        types = ", ".join(t.capitalize() for t in candidate["types"])
        click.echo(f"  Found a wallpaper for {candidate['name'].capitalize()} ({types})!")

        click.echo("Downloading...")
        path = download_wallpaper(url, candidate["name"])

        click.echo("Applying wallpaper...")
        set_gnome_wallpaper(path)
        save_state(today, index)

        click.echo(
            f"Done! Today's Pokémon: #{candidate['id']:03d} "
            f"{candidate['name'].capitalize()} ({types})."
        )
        return

    raise click.ClickException("No more wallpapers found for today.")


@main.command()
def run():
    """Fetch and apply today's Pokémon wallpaper."""
    today = date.today()
    click.echo("Selecting today's Pokémon...")
    _apply_from_index(today, start_index=0)


@main.command()
def next():
    """Skip to the next Pokémon wallpaper for today."""
    today = date.today()
    current_index = load_state(today)
    click.echo("Finding the next Pokémon...")
    _apply_from_index(today, start_index=current_index + 1)


@main.command()
def install():
    """Install a systemd user timer to run daily at 08:00."""
    try:
        _install()
        click.echo("Timer installed. Wallpaper will update daily at 08:00.")
        click.echo("Run 'pokemon-wallpaper run' to apply today's wallpaper right now.")
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
def uninstall():
    """Remove the systemd user timer."""
    try:
        _uninstall()
        click.echo("Timer removed.")
    except Exception as e:
        raise click.ClickException(str(e))
