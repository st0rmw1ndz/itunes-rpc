import time

from pypresence import Presence

from tunedisplay.artwork.manager import ArtworkManager
from tunedisplay.tunedata import TunePlayer, TunePlayerState, TuneReport


class TuneDisplay:
    def __init__(self, rpc: Presence, artwork_manager: ArtworkManager) -> None:
        self.rpc = rpc
        self.artwork_manager = artwork_manager

        self.itunes = TunePlayer()
        self.saved_track = TuneReport.create_empty()

    def update_track(self, current_track: TuneReport) -> TuneReport:
        if current_track != TuneReport.create_empty():
            if current_track == self.saved_track:
                current_track.artwork_url = self.saved_track.artwork_url
            else:
                current_track.artwork_url = self.artwork_manager.get_artwork_url(current_track)
        return current_track

    def update_rpc(self, current_track: TuneReport) -> None:
        if current_track == TuneReport.create_empty():
            if self.saved_track is not None:
                self.rpc.update(**current_track.to_rpc_data())
                self.saved_track = None
            return

        if (
            (self.saved_track is None)
            or (
                current_track.state == TunePlayerState.PLAYING
                and abs(current_track.position - self.saved_track.position) > 5
            )
            or (current_track != self.saved_track)
        ):
            self.rpc.update(**current_track.to_rpc_data())
            self.saved_track = current_track

    def run(self, sleep_seconds: int) -> None:
        while True:
            current_track = self.itunes.create_report()
            current_track = self.update_track(current_track)
            self.update_rpc(current_track)
            time.sleep(sleep_seconds)

    def connect(self) -> None:
        self.rpc.connect()
        self.itunes.dispatch()

    def close(self) -> None:
        if self.rpc:
            self.rpc.close()
