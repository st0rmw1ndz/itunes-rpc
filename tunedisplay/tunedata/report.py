import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Type

import httpx
from bs4 import BeautifulSoup

from tunedisplay.tunedata.playerstate import TunePlayerState


@dataclass
class TuneReport:
    name: str
    artist: str
    album: str
    year: int
    artwork: Any | None
    artwork_url: str
    duration: int
    track_id: int
    position: int
    state: TunePlayerState

    def __eq__(self, other: Type["TuneReport"]) -> bool:
        if not isinstance(other, TuneReport):
            return False

        return self.track_id == other.track_id and self.state == other.state

    @property
    def lastfm_url(self) -> str | None:
        base_url = "https://www.last.fm/music/{artist}/_/{track}"
        url = base_url.format(
            artist=urllib.parse.quote(self.artist.replace(" ", "+")),
            track=urllib.parse.quote(self.name.replace(" ", "+")),
        )
        page = httpx.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        return url if "Page Not Found" not in soup.title.string else None

    def to_rpc_data(self) -> dict:
        rpc_data = {}

        if self.state == TunePlayerState.STOPPED:
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

        if self.state == TunePlayerState.PLAYING:
            rpc_data["start"] = max(0, int(time.time()) - self.position)
            rpc_data["end"] = max(0, int(time.time()) + (self.duration - self.position))

        # if self.exists_on_lastfm:
        #     rpc_data["buttons"] = [
        #         {"label": "Last.fm", "url": self.lastfm_url},
        #     ]

        return rpc_data

    @staticmethod
    def create_empty() -> Type["TuneReport"]:
        return TuneReport(
            name="",
            artist="",
            album="",
            year=0,
            artwork=None,
            artwork_url="",
            duration=0,
            track_id=0,
            position=0,
            state=TunePlayerState.STOPPED,
        )
