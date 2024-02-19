import mimetypes
from pathlib import Path

import httpx

from tunedisplay.artwork.uploaders.base import ArtworkUploader


class OwoArtworkUploader(ArtworkUploader):
    def __init__(self, client: httpx.Client, auth: str) -> None:
        super().__init__(client, "https://api.awau.moe/upload/pomf", auth)

    def upload(self, file: Path) -> str:
        with file.open(mode="rb") as stream:
            mimetype = mimetypes.guess_type(file.name)[0]

            files = {"files[]": (file.name, stream, mimetype)}
            headers = {"Authorization": self.auth}

            response = self.multipart_post(files, headers=headers)

        return response.json()["files"][0]["url"]
