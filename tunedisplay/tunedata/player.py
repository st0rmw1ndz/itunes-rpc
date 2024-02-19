import win32com.client

from tunedisplay.tunedata.playerstate import TunePlayerState
from tunedisplay.tunedata.report import TuneReport


class TunePlayer:
    def __init__(self) -> None:
        self._player = None

    def dispatch(self) -> None:
        self._player = win32com.client.Dispatch("iTunes.Application")

    @property
    def state(self) -> TunePlayerState:
        if self._player.PlayerState != 0:
            return TunePlayerState.PLAYING
        if self._player.CurrentTrack is None:
            return TunePlayerState.STOPPED
        return TunePlayerState.PAUSED

    def create_report(self) -> TuneReport | None:
        if not self._player:
            return None

        if self.state == TunePlayerState.STOPPED:
            return TuneReport.create_empty()

        current_track = self._player.CurrentTrack

        return TuneReport(
            name=current_track.Name,
            artist=current_track.Artist,
            album=current_track.Album,
            year=current_track.Year,
            artwork=current_track.Artwork.Item(1) if current_track.Artwork else None,
            artwork_url="",
            duration=current_track.Duration,
            track_id=current_track.TrackID,
            position=self._player.PlayerPosition,
            state=self.state,
        )
