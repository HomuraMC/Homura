__all__ = (
    "ServerBindingException",
    "CloseConnection",
    "InvalidPacketID",
)


class ServerBindingException(Exception):
    def __init__(self, address: str, port: str):
        super().__init__(f"Server binding failed on {address}:{port}")


class CloseConnection(Exception):
    pass


class InvalidPacketID(Exception):
    pass
