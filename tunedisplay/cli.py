import os
from pathlib import Path

import click
import httpx
from pypresence import Presence

from tunedisplay.app import TuneDisplay
from tunedisplay.artwork.manager import ArtworkManager
from tunedisplay.artwork.uploaders import CatboxArtworkUploader


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-c",
    "--client-id",
    type=int,
    default=1159337432840421447,
    help="The client ID of the Discord developer application to use.",
)
@click.option(
    "-s",
    "--sleep-seconds",
    type=int,
    default=1,
    help="The interval of when to update the Rich Presence.",
)
def cli(client_id: int, sleep_seconds: int) -> None:
    """Discord Rich Presence using data from iTunes.

    Copyright (c) 2024 frosty.
    """
    data_folder = Path(os.getenv("LOCALAPPDATA")).joinpath("TuneDisplay")
    data_folder.mkdir(exist_ok=True)

    rpc = Presence(client_id)

    with httpx.Client() as client:
        artwork_uploader = CatboxArtworkUploader(client)
        artwork_manager = ArtworkManager(data_folder, artwork_uploader)

        try:
            app = TuneDisplay(rpc, artwork_manager)
            app.connect()
            app.run(sleep_seconds)
        except Exception as e:
            print(e)
            app.close()
