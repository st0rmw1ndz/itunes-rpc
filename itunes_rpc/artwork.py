# TODO: Rework into an abstract class so that it can be used with other services

__all__ = ["get_artwork_url"]

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Tuple, Union

from loguru import logger
from PIL import Image
from pyimgur import Imgur

from .itunes import ItunesReport

IMGUR_CLIENT_ID = "865213c7a7bab4f"
ARTWORK_SIZE = (512, 512)

artwork_path = Path.cwd() / "data/artwork.jpg"
hashes_path = Path.cwd() / "data/hashes.json"


def save_artwork(artwork: Any) -> bool:
    """Saves the artwork to a file and resizes it.

    :param artwork: Artwork to use
    :return: Whether or not it was successful
    """
    try:
        artwork.SaveArtworkToFile(artwork_path)

        im = Image.open(artwork_path)
        im = im.resize(ARTWORK_SIZE)
        im.save(artwork_path)

        return True
    except Exception as e:
        logger.warning(f"Unable to save artwork, does the track have artwork?\n{e}")
        return False


def upload_artwork() -> str:
    """Uploads the artwork to Imgur.

    :return: Imgur URL
    """
    im = Imgur(IMGUR_CLIENT_ID)
    uploaded_image = im.upload_image(artwork_path)
    artwork_url = uploaded_image.link
    logger.info(f"Uploaded artwork to {artwork_url}")
    return artwork_url


def dump_hash(url: str) -> None:
    """Dumps the current hash to the hashes file, along with the artwork URL.

    :param url: URL to dump
    """
    with hashes_path.open(mode="r") as f:
        hashes = json.load(f)

    hashes[get_current_md5()] = url

    with hashes_path.open(mode="w") as f:
        json.dump(hashes, f, indent=4)

    logger.info(f"Dumped hash {get_current_md5()} to hashes file with URL {url}")


def get_current_md5() -> str:
    """Gets the current MD5 hash of the artwork.

    :return: Current MD5 hash
    """
    with artwork_path.open(mode="rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def check_hash_exists() -> bool:
    """Checks if the current hash exists in the hashes file.

    :return: Whether or not the hash exists
    """
    with hashes_path.open(mode="r") as f:
        hashes = json.load(f)

    return hashes.get(get_current_md5(), None) is not None


def get_current_url() -> str:
    """Gets the current artwork URL.

    :return: Current artwork URL
    """
    with hashes_path.open(mode="r") as f:
        hashes = json.load(f)

    return hashes[get_current_md5()] if check_hash_exists() else None


def get_artwork_url(report: Union[ItunesReport, None]) -> Union[str, None]:
    """Gets the artwork URL for the report.

    :param report: Report to get artwork URL for
    :return: Artwork URL
    """
    if report.artwork is None:
        report.artwork_url = None
        return

    if not save_artwork(report.artwork):
        return None

    if check_hash_exists():
        return get_current_url()
    else:
        url = upload_artwork()
        dump_hash(url)
        return url
