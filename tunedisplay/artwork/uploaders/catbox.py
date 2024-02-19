import mimetypes
from pathlib import Path

import httpx

from tunedisplay.artwork.uploaders.base import ArtworkUploader


class CatboxArtworkUploader(ArtworkUploader):
    def __init__(self, client: httpx.Client) -> None:
        super().__init__(client, "https://catbox.moe/user/api.php")

    def upload(self, file: Path) -> str:
        with file.open(mode="rb") as stream:
            mimetype = mimetypes.guess_type(file.name)[0]

            files = {"fileToUpload": (file.name, stream, mimetype)}
            data = {"reqtype": "fileupload"}

            response = self.multipart_post(files, data=data)

        return response.text
