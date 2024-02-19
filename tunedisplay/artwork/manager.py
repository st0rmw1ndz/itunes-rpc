import hashlib
import sqlite3
from pathlib import Path
from typing import Tuple

from httpx import HTTPError
from PIL import Image

from tunedisplay.artwork.uploaders import ArtworkUploader
from tunedisplay.tunedata import TuneReport


class ArtworkManager:
    ARTWORK_SIZE = (512, 512)

    def __init__(self, directory: Path, uploader: ArtworkUploader) -> None:
        self.artwork_path = directory.joinpath("artwork.jpg")
        self.database_path = directory.joinpath("artwork.db")
        self.uploader = uploader

        self.conn, self.cursor = self.initialize_db()

    def initialize_db(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        conn = sqlite3.connect(self.database_path.resolve())
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS artwork (
                md5 TEXT PRIMARY KEY,
                url TEXT
            )
            """
        )
        conn.commit()

        return conn, cursor

    def save_artwork(self, report: TuneReport) -> None:
        report.artwork.SaveArtworkToFile(self.artwork_path)
        Image.open(self.artwork_path).resize(self.ARTWORK_SIZE).save(self.artwork_path)

    def get_current_hash(self) -> str:
        with self.artwork_path.open(mode="rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def check_hash_exists(self, md5: str) -> bool:
        self.cursor.execute("SELECT url FROM artwork WHERE md5=?", (md5,))
        return self.cursor.fetchone() is not None

    def get_current_url(self, md5: str) -> str:
        self.cursor.execute("SELECT url FROM artwork WHERE md5=?", (md5,))
        result = self.cursor.fetchone()
        return result[0] if result else ""

    def dump_hash(self, md5: str, url: str) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO artwork (md5, url) VALUES (?, ?)",
            (md5, url),
        )
        self.conn.commit()

    def get_artwork_url(self, report: TuneReport) -> str:
        if report.artwork is None:
            return ""

        try:
            self.save_artwork(report)
        except Exception:
            return ""

        md5 = self.get_current_hash()

        if self.check_hash_exists(md5):
            return self.get_current_url(md5)

        try:
            url = self.uploader.upload(self.artwork_path)
            self.dump_hash(md5, url)
            print(url)
            return url
        except HTTPError:
            return ""
