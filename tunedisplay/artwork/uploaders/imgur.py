import mimetypes
from pathlib import Path

import httpx

from tunedisplay.artwork.uploaders.base import ArtworkUploader


class ImgurArtworkUploader(ArtworkUploader):
    def __init__(self, client: httpx.Client) -> None:
        super().__init__(client, "https://api.imgur.com/3/image", "865213c7a7bab4f")

    def upload(self, file: Path) -> str:
        with file.open(mode="rb") as stream:
            mimetype = mimetypes.guess_type(file.name)[0]

            files = {"image": (file.name, stream, mimetype)}
            headers = {"Authorization": f"Client-ID {self.auth}"}

            response = self.multipart_post(files, headers=headers)

        return response.json()["data"]["link"]
