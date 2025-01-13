import asyncio
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.base import CipherContext


class Player:
    def __init__(
        self,
        *,
        id: UUID,
        name: str,
        encryptor: CipherContext,
        decryptor: CipherContext,
        writer: asyncio.StreamWriter,
        reader: asyncio.StreamReader,
        entityId: int
    ):
        self.id = id
        self.name = name
        self.encryptor = encryptor
        self.decryptor = decryptor
        self.writer = writer
        self.reader = reader
        self.entityId = entityId
