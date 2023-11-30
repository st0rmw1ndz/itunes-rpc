import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from hashlib import md5
from typing import Any, Union

import psutil
import win32com.client
from PIL import Image
from pyimgur import Imgur
from pypresence import Presence

artwork_path = os.getcwd() + "\\artwork.jpg"
hashes_path = os.getcwd() + "\\hashes.json"
client_id = "865213c7a7bab4f"


class PlayerState(Enum):
    STOPPED = "stopped"
    PAUSED = "paused"
    PLAYING = "playing"


@dataclass
class ItunesReport:
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

    def create_empty():
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

    def __eq__(self, other: Any):
        if not isinstance(other, ItunesReport):
            return False

        return self.track_id == other.track_id and self.state == other.state

    def create_rpc_data(self):
        rpc_data = {}

        rpc_data["details"] = self.name
        rpc_data["small_image"] = self.state.value
        rpc_data["small_text"] = self.state.value.capitalize()

        if self.artist:
            rpc_data["state"] = f"by {self.artist}"
        else:
            rpc_data["state"] = None

        if self.album and self.year:
            rpc_data["large_text"] = f"{self.album} ({self.year})"
        elif self.album:
            rpc_data["large_text"] = self.album
        else:
            rpc_data["large_text"] = None

        if self.artwork_url:
            rpc_data["large_image"] = self.artwork_url
        else:
            rpc_data["large_image"] = "music-2013"

        if self.state == PlayerState.PLAYING:
            rpc_data["start"] = int(time.time()) - self.position
            rpc_data["end"] = int(time.time()) + (self.duration - self.position)

        return rpc_data


def save_and_resize(artwork) -> bool:
    try:
        artwork.SaveArtworkToFile(artwork_path)

        im = Image.open(artwork_path)
        im = im.resize((512, 512))
        im.save(artwork_path)

        return True
    except Exception as e:
        print(f"Unable to save artwork, does the track have artwork?\n{e}")
        return False


def upload_and_dump() -> None:
    im = Imgur(client_id)
    uploaded_image = im.upload_image(artwork_path)
    link = uploaded_image.link

    with open(hashes_path, "r") as f:
        hashes = json.load(f)

    hashes[get_current_md5()] = link

    with open(hashes_path, "w") as f:
        json.dump(hashes, f, indent=4)


def get_current_md5():
    with open(artwork_path, "rb") as f:
        return md5(f.read()).hexdigest()


def check_hash_exists():
    with open(hashes_path, "r") as f:
        hashes = json.load(f)

    return hashes.get(get_current_md5(), None) is not None


def get_current_url():
    with open(hashes_path, "r") as f:
        hashes = json.load(f)

    return hashes[get_current_md5()] if check_hash_exists() else None


def update_artwork_wrapper(report: Union[ItunesReport, None]) -> None:
    if report.artwork is None:
        report.artwork_url = None
        return

    if not save_and_resize(report.artwork):
        report.artwork_url = None
        return

    if check_hash_exists():
        report.artwork_url = get_current_url()
    else:
        upload_and_dump()
        report.artwork_url = get_current_url()

    return


class ItunesPlayer:
    def __init__(self):
        self._player = None

    def dispatch(self) -> win32com.client.CDispatch:
        self._player = win32com.client.Dispatch("iTunes.Application")

    @property
    def state(self) -> PlayerState:
        if self._player.PlayerState == 0:
            if self._player.CurrentTrack is None:
                return PlayerState.STOPPED
            else:
                return PlayerState.PAUSED
        else:
            return PlayerState.PLAYING

    @property
    def is_running(self) -> bool:
        return "iTunes.exe" in (p.name() for p in psutil.process_iter())

    def create_report(self) -> Union[ItunesReport, None]:
        if not self.is_running or not self._player:
            return None

        current_track = self._player.CurrentTrack

        return ItunesReport(
            name=current_track.Name,
            artist=current_track.Artist,
            album=current_track.Album,
            year=current_track.Year,
            artwork=current_track.Artwork.Item(1) if current_track.Artwork else None,
            artwork_url=None,
            duration=current_track.Duration,
            track_id=current_track.TrackID,
            position=self._player.PlayerPosition,
            state=self.state,
        )


class RPCHandler:
    def __init__(self, client_id: int):
        self._client = Presence(client_id)
        self._client.connect()

    def update_idling(self) -> None:
        self._client.update(large_image="music-2013", state="Idling")

    def update_report(self, report: ItunesReport) -> None:
        self._client.update(**report.create_rpc_data())


if __name__ == "__main__":
    itunes: Union[ItunesPlayer, None] = None
    rpc: Union[RPCHandler, None] = None
    saved_track: Union[ItunesReport, None] = None

    itunes = ItunesPlayer()
    itunes.dispatch()
    rpc = RPCHandler(1159337432840421447)

    while True:
        try:
            current_track = itunes.create_report()
        except AttributeError:
            current_track = None

        if current_track == saved_track and current_track is not None:
            current_track.artwork_url = saved_track.artwork_url
        elif current_track is not None:
            update_artwork_wrapper(current_track)

        if saved_track is None:
            saved_track = ItunesReport.create_empty()

        if itunes.state == PlayerState.STOPPED:
            if saved_track is not None:
                rpc.update_idling()
                saved_track = None

            time.sleep(1)
            continue

        if (
            current_track.state == PlayerState.PLAYING
            and abs(current_track.position - saved_track.position) > 5
        ):
            rpc.update_report(current_track)
            saved_track = current_track
        elif current_track != saved_track:
            rpc.update_report(current_track)
            saved_track = current_track

        time.sleep(1)
