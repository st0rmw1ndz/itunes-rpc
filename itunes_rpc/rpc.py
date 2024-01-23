from pypresence import Presence

from itunes_rpc.itunes import ItunesReport


class RPCHandler:
    def __init__(self, client_id: int) -> None:
        self._client = Presence(client_id)
        self._client.connect()

    def update_report(self, report: ItunesReport) -> None:
        self._client.update(**report.to_rpc_data())

    def close(self) -> None:
        self._client.close()

    def clear(self) -> None:
        self._client.clear()
