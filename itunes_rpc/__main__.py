import sys
import time
from typing import Union

from .artwork import get_artwork_url
from .data import ensure_structure_ready
from .itunes import ItunesPlayer, ItunesReport, PlayerState
from .rpc import RPCHandler

itunes: Union[ItunesPlayer, None] = None
rpc: Union[RPCHandler, None] = None
saved_track: Union[ItunesReport, None] = None

SLEEP_TIME = 1
DISCORD_CLIENT_ID = 1159337432840421447


def initialize() -> None:
    """Initializes the program."""

    global itunes, rpc, saved_track

    ensure_structure_ready()

    itunes = ItunesPlayer()
    itunes.dispatch()
    rpc = RPCHandler(DISCORD_CLIENT_ID)
    saved_track = ItunesReport.create_empty()


def main_loop() -> None:
    global saved_track

    current_track = itunes.create_report()

    if current_track is None:
        return

    if current_track != ItunesReport.create_empty():
        if current_track == saved_track:
            current_track.artwork_url = saved_track.artwork_url
        else:
            current_track.artwork_url = get_artwork_url(current_track)

    if current_track == ItunesReport.create_empty():
        if saved_track is not None:
            rpc.update_report(current_track)
            saved_track = None
            return
        else:
            return

    if saved_track is None:
        rpc.update_report(current_track)
        saved_track = current_track
    elif (
        current_track.state == PlayerState.PLAYING
        and abs(current_track.position - saved_track.position) > 5
    ):
        rpc.update_report(current_track)
        saved_track = current_track
    elif current_track != saved_track:
        rpc.update_report(current_track)
        saved_track = current_track


def main() -> int:
    try:
        initialize()

        while True:
            main_loop()
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        if rpc:
            rpc.close()

        print("Closing...")
        return 0


if __name__ == "__main__":
    sys.exit(main())
