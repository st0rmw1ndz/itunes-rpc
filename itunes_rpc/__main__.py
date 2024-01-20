import time

from itunes_rpc.artwork import get_artwork_url
from itunes_rpc.data import ensure_structure_ready
from itunes_rpc.itunes import ItunesPlayer, ItunesReport, PlayerState
from itunes_rpc.rpc import RPCHandler


SLEEP_TIME = 1
DISCORD_CLIENT_ID = 1159337432840421447


class ItunesRpc:
    def __init__(self) -> None:
        ensure_structure_ready()
        self.itunes = ItunesPlayer()
        self.itunes.dispatch()
        self.rpc = RPCHandler(DISCORD_CLIENT_ID)
        self.saved_track = ItunesReport.create_empty()

    def start(self) -> None:
        current_track = self.itunes.create_report()

        if current_track is None:
            return

        if current_track != ItunesReport.create_empty():
            if current_track == self.saved_track:
                current_track.artwork_url = self.saved_track.artwork_url
            else:
                current_track.artwork_url = get_artwork_url(current_track)

        if current_track == ItunesReport.create_empty():
            if self.saved_track is not None:
                self.rpc.update_report(current_track)
                self.saved_track = None
                return
            else:
                return

        if self.saved_track is None:
            self.rpc.update_report(current_track)
            self.saved_track = current_track
        elif (
            current_track.state == PlayerState.PLAYING
            and abs(current_track.position - self.saved_track.position) > 5
        ):
            self.rpc.update_report(current_track)
            self.saved_track = current_track
        elif current_track != self.saved_track:
            self.rpc.update_report(current_track)
            self.saved_track = current_track

    def close_rpc(self) -> None:
        if self.rpc:
            self.rpc.close()


def main() -> None:
    try:
        itunes_rpc = ItunesRpc()
        while True:
            itunes_rpc.start()
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        itunes_rpc.close_rpc()
        print("Closing...")


if __name__ == "__main__":
    main()
