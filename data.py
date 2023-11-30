from pathlib import Path


def ensure_structure_ready() -> None:
    if not Path("data").exists():
        Path("data").mkdir()

    if not Path("data/hashes.json").exists():
        Path("data/hashes.json").touch()
