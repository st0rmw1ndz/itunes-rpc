__all__ = ["ItunesPlayer", "ItunesReport", "PlayerState"]

import time
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Any, Union

import psutil
import pypresence
import requests
import win32com.client
from bs4 import BeautifulSoup


class PlayerState(Enum):
    """Represents the state of the player.

    The values are used as the small image key in the RPC data.
    """
    STOPPED = "stopped"
    PAUSED = "paused"
    PLAYING = "playing"


@dataclass
class ItunesReport:
    """Represents a report of the current track in iTunes.

    If the player is stopped, all fields will be empty.
    """
    name: str
    artist: str
    album: str
    year: int
    artwork: Any
    artwork_url: str
    duration: int
    track_id: int
    position: int
    state: PlayerState

    def __eq__(self, other: "ItunesReport") -> bool:
        if not isinstance(other, ItunesReport):
            return False

        return self.track_id == other.track_id and self.state == other.state

    @staticmethod
    def create_empty() -> "ItunesReport":
        """Creates an empty report.

        :return: Empty report
        """
        return ItunesReport(
            name="",
            artist="",
            album="",
            year=0,
            artwork=None,
            artwork_url="",
            duration=0,
            track_id=0,
            position=0,
            state=PlayerState.STOPPED,
        )

    @property
    def lastfm_url(self) -> str:
        """Gets the Last.fm URL for the track.

        :return: Last.fm URL
        """
        return f"https://www.last.fm/music/{urllib.parse.quote(self.artist.replace(' ', '+'))}/_/{urllib.parse.quote(self.name.replace(' ', '+'))}"

    @property
    def exists_on_lastfm(self) -> bool:
        """Checks if the track exists on Last.fm.

        :return: Whether or not the track exists
        """
        page = requests.get(self.lastfm_url)
        soup = BeautifulSoup(page.content, "html.parser")

        return "Page Not Found" not in soup.title.string

    def to_rpc_data(self) -> dict[str, Union[str, int]]:
        """Creates a dictionary of the report's data to be used by the RPC client.

        :return: RPC data
        """
        rpc_data = {}

        if self.state == PlayerState.STOPPED:
            rpc_data["details"] = "Idling"
            rpc_data["large_image"] = "itunes-12"

            return rpc_data

        rpc_data["details"] = self.name
        rpc_data["small_image"] = self.state.value
        rpc_data["small_text"] = self.state.value.capitalize()

        if self.artist:
            rpc_data["state"] = f"by {self.artist}"
        else:
            rpc_data["state"] = ""

        if self.album and self.year:
            rpc_data["large_text"] = f"{self.album} ({self.year})"
        elif self.album:
            rpc_data["large_text"] = self.album
        else:
            rpc_data["large_text"] = ""

        if self.artwork_url:
            rpc_data["large_image"] = self.artwork_url
        else:
            rpc_data["large_image"] = "itunes-12"

        if self.state == PlayerState.PLAYING:
            rpc_data["start"] = max(0, int(time.time()) - self.position)
            rpc_data["end"] = max(0, int(time.time()) + (self.duration - self.position))

        if self.exists_on_lastfm:
            rpc_data["buttons"] = [
                {"label": "Last.fm", "url": self.lastfm_url},
            ]

        return rpc_data


class ItunesPlayer:
    """Represents the iTunes player."""

    def __init__(self) -> None:
        self._player = None

    def dispatch(self) -> None:
        """Dispatches the iTunes COM."""

        self._player = win32com.client.Dispatch("iTunes.Application")

    @property
    def state(self) -> PlayerState:
        """Gets the state of the player.

        :return: Player state
        """
        if self._player.PlayerState == 0:
            if self._player.CurrentTrack is None:
                return PlayerState.STOPPED
            else:
                return PlayerState.PAUSED
        else:
            return PlayerState.PLAYING

    @property
    def is_running(self) -> bool:
        """Gets whether or not iTunes is running.

        :return: Whether or not iTunes is running
        """
        return "iTunes.exe" in (p.name() for p in psutil.process_iter())

    def create_report(self) -> Union[ItunesReport, None]:
        """Creates a report of the current track.

        :return: Current track report
        """
        if not self.is_running or not self._player:
            return None

        if self.state == PlayerState.STOPPED:
            return ItunesReport.create_empty()

        current_track = self._player.CurrentTrack

        return ItunesReport(
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
