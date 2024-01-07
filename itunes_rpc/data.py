from pathlib import Path


def ensure_structure_ready() -> None:
    data_dir = Path("data")
    hashes_path = Path("data/hashes.json")

    if not data_dir.exists():
        data_dir.mkdir()

    if not hashes_path.exists():
        with hashes_path.open(mode="w") as f:
            f.write("{}")
