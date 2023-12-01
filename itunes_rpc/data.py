from pathlib import Path


def ensure_structure_ready() -> None:
    data_dir: Path = Path("data")
    hashes_path: Path = Path("data/hashes.json")

    # Creating the 'data' directory if it doesn't exist
    if not data_dir.exists():
        data_dir.mkdir()

    # Creating the 'hashes.json' file if it doesn't exist,
    # and writing an empty JSON object to it
    if not hashes_path.exists():
        with hashes_path.open(mode="w") as f:
            f.write("{}")
