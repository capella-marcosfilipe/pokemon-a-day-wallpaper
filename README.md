# Pokémon-a-day Wallpaper

![Pokémon-a-day Wallpaper](https://raw.githubusercontent.com/capella-marcosfilipe/pokemon-a-day-wallpaper/refs/heads/main/art.png)

As a big fan of Bing Wallpaper, I wanted something similar for my desktop but featuring Pokémon fanart. So I built this tool to automatically set a new Pokémon wallpaper every day, sourced from the amazing community on Wallhaven.

**Pokémon-a-day Wallpaper** is a CLI tool that randomly selects a Pokémon (seeded by the date, so it's consistent throughout the day) and a high-quality fan art wallpaper (1920x1080 or higher) is fetched from [Wallhaven](https://wallhaven.cc) and applied to your desktop. If you don't like the wallpaper, just run `next` to get a different one — it will still change automatically the following day.

## Requirements

- Windows 10/11 or Ubuntu with GNOME
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

### Skip to a different wallpaper

Don't like today's pick? Get the next one:

```bash
pokemon-wallpaper next
```

You can run `next` as many times as you want throughout the day. The wallpaper will still automatically reset to a fresh Pokémon the following day.

### Go back to a previous wallpaper

```bash
pokemon-wallpaper previous
```

Navigates back through your wallpaper history. The session is paused while browsing — run `refresh` to return to today's wallpaper.

### Resume today's wallpaper

```bash
pokemon-wallpaper refresh
```

### Schedule daily automatic updates

Sets up the wallpaper to update every day at 08:00 and to apply automatically on login:

```bash
pokemon-wallpaper install
```

On **Linux**, this installs a systemd user timer and an XDG autostart entry.  
On **Windows**, this creates a Task Scheduler entry and a registry Run key — no admin rights required.

After installing, apply today's wallpaper right away:

```bash
pokemon-wallpaper run
```

### Remove the automatic schedule

```bash
pokemon-wallpaper uninstall
```

### Browse your wallpaper history

```bash
pokemon-wallpaper list-wallpapers
```

### Open the wallpaper folder

```bash
pokemon-wallpaper open-folder
```

Opens the folder where wallpapers are downloaded in your file manager.

### Configure storage settings

```bash
pokemon-wallpaper config
```

Shows the current storage mode. Use flags to change it:

```bash
pokemon-wallpaper config --keep-images     # Save all wallpapers locally
pokemon-wallpaper config --no-keep-images  # Keep only the 3 most recent on disk
```

On first run you will be prompted interactively to choose a storage mode.

## Wallpaper storage

Downloaded wallpapers and history are cached at:

| Platform | Path |
|----------|------|
| Linux | `~/.local/share/pokemon-wallpaper/` |
| Windows | `%LOCALAPPDATA%\pokemon-wallpaper\` |

You can choose to keep all wallpapers locally or use a rolling cache that retains only the 3 most recent files on disk (history is always preserved).

## License

MIT

## Author

[Marcos Filipe Capella](https://github.com/capella-marcosfilipe) - I'm a Software Engineer and Pokémon enthusiast. I created this project for my work laptop with the help of Claude Code and further refining it by myself.
