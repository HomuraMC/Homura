import struct
import zlib
from typing import Any, Optional

from cryptography.hazmat.primitives.ciphers.base import CipherContext

from core.utils import decodeVarInt, encodeVarInt


class Data:
    def __init__(self, data: Optional[bytes] = None):
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

    def packVarInt(cls, number, max_bits=32):
        number_min = -1 << (max_bits - 1)
        number_max = +1 << (max_bits - 1)
        if not (number_min <= number < number_max):
            raise ValueError(
                f"varint does not fit in range: {number_min:d} <= {number:d} < {number_max:d}"
            )

        if number < 0:
            number += 1 << 32

        out = b""
        for i in range(10):
            b = number & 0x7F
            number >>= 7
            out += struct.pack("B", b | (0x80 if number > 0 else 0))
            if number == 0:
                break
        return out

    def getAllForSend(
        self,
        *,
        encryptor: Optional[CipherContext] = None,
        compressionThreshold: int = -1,
    ):
        data = encodeVarInt(len(self.data)) + self.data
        if compressionThreshold >= 0:
            if len(data) <= compressionThreshold:
                data = encodeVarInt(len(data)) + zlib.compress(data)
            else:
                data = encodeVarInt(0) + data
        return encryptor.update(data) if encryptor else data
