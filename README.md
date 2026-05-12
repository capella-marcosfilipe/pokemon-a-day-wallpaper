# Pokémon-a-day Wallpaper

![Pokémon-a-day Wallpaper](/art.png)

As a big fan of Bing Wallpaper, I wanted something similar for my GNOME desktop but feturing Pokémon fanart. So I built this tool to automatically set a new Pokémon wallpaper every day, sourced from the amazing community on Wallhaven.

**Pokémon-a-day Wallpaper** is a CLI tool that randomly selects a Pokémon (seeded by the date, so it's consistent throughout the day) and a high-quality fan art wallpaper (1920x1080 or higher) is fetched from [Wallhaven](https://wallhaven.cc) and applied to your desktop. If you don't like the wallpaper, just run `next` to get a different one — it will still change automatically the following day.

## Requirements

- GNOME desktop environment
- Python 3.10+
- Internet connection

## Installation

```bash
pip install pokemon-a-day-wallpaper
```

## Usage

### Apply today's wallpaper immediately

```bash
pokemon-wallpaper run
```

### Skip to a different wallpaper (same day)

Don't like today's pick? Get the next one:

```bash
pokemon-wallpaper next
```

You can run `next` as many times as you want throughout the day. The wallpaper will still automatically reset to a fresh Pokémon the following day.

### Schedule daily automatic updates

Installs a systemd user timer that runs every day at 08:00:

```bash
pokemon-wallpaper install
```

After installing the timer, apply today's wallpaper right away:

```bash
pokemon-wallpaper run
```

### Remove the automatic schedule

```bash
pokemon-wallpaper uninstall
```

## Wallpaper storage

Downloaded wallpapers are cached at:

```text
~/.local/share/pokemon-wallpaper/
```

## License

MIT

## Author

[Marcos Filipe Capella](https://github.com/capella-marcosfilipe) - I'm a Software Engineer and Pokémon enthusiast. I created this project for my work laptop with the help of Claude Code and further refining it by myself.
