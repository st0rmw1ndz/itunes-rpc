from abc import ABC, abstractmethod
from pathlib import Path

import httpx


class ArtworkUploader(ABC):
    def __init__(self, client: httpx.Client, upload_url: str, auth: str | None = None) -> None:
        self.client = client
        self.upload_url = upload_url
        self.auth = auth

    @abstractmethod
    def upload(self, file: Path) -> str:
        raise NotImplementedError

    def multipart_post(self, files: dict, *, data: str | None = None, headers: str | None = None) -> httpx.Response:
        response = self.client.post(self.upload_url, files=files, data=data, headers=headers)
        response.raise_for_status()
        return response
