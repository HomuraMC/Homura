import struct
from typing import Any
from core.utils import decodeVarInt, encodeVarInt


class Data:
    def __init__(self, data: bytes = None):
        self.data = data or bytes()
        self.position = 0

    def getVarInt(self) -> int:
        received = b""
        for r in self.data[self.position :]:
            received += bytes([r])
            self.position += 1
            if not r & 128:
                break
        return decodeVarInt(received)

    def getString(self) -> str:
        received = b""
        for r in self.data[self.position :]:
            received += bytes([r])
            self.position += 1
            if not r & 128:
                break
        size = decodeVarInt(received)
        stringData = self.data[self.position : self.position + size].decode("utf-8")
        self.position += size
        return stringData

    def getBinary(self) -> str:
        received = b""
        for r in self.data[self.position :]:
            received += bytes([r])
            self.position += 1
            if not r & 128:
                break
        size = decodeVarInt(received)
        binaryData = self.data[self.position : self.position + size]
        self.position += size
        return binaryData

    def getUnPackedData(self, fmt: str, size: int) -> Any:
        data = struct.unpack(fmt, self.data[self.position : self.position + size])[0]
        self.position += size
        return data

    def getData(self, size: int) -> Any:
        self.position += size
        return self.data[self.position - size : self.position]

    def addData(self, data: Any):
        self.data += data
        return self

    def addDataWithLength(self, data: Any):
        self.data += encodeVarInt(len(data)) + data
        return self

    def getAllForSend(self, *, encryptor=None):
        if encryptor:
            return encryptor.update(encodeVarInt(len(self.data)) + self.data)
        else:
            return encodeVarInt(len(self.data)) + self.data
