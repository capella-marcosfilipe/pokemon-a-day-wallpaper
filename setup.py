from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="pokemon-a-day-wallpaper",
    version="0.3.0",
    author="Marcos Filipe Capella",
    author_email="marcosfilipe.gc@gmail.com",
    description="Sets a daily Pokémon fan art wallpaper on Windows and Ubuntu GNOME",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/capella-marcosfilipe/pokemon-a-day-wallpaper",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27",
        "click>=8.1",
    ],
    entry_points={
        "console_scripts": [
            "pokemon-wallpaper=pokemon_wallpaper.cli:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "Topic :: Desktop Environment",
    ],
    keywords=["pokemon", "wallpaper", "gnome", "ubuntu", "windows", "automation"],
)
