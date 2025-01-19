import asyncio
import hashlib
import logging
import os
import random
import string
import struct
from typing import List
from uuid import UUID
from datetime import datetime

import orjson
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import ciphers, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import algorithms, modes
from httpx import AsyncClient

from .config import Config
from .objects.data import Data
from .objects.player import Player
from .utils import decodeVarInt, encodeVarInt, receiveData


class Server:
    def __init__(self):
        self.key = rsa.generate_private_key(
            public_exponent=65537, key_size=1024, backend=default_backend()
        )
        self.publicKey = self.key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.logger = logging.getLogger("HomuraMC")
        self.config = Config().config
        self.http = AsyncClient()
        self.players: List[Player] = []

    async def run(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = Data(await receiveData(reader))
        packetId = data.getVarInt()
        if packetId != 0:
            writer.close()
            return
        protocolVersion = data.getVarInt()
        address = data.getString()
        port = data.getUnPackedData(">H", 2)
        nextState = data.getVarInt()
        if nextState == 1:
            await self.sendServerDetails(reader, writer, address, port)
        elif nextState == 2:
            await self.loginForGame(reader, writer, address, port, protocolVersion)
        else:
            writer.close()
            return

    async def sendServerDetails(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        address: str,
        port: int,
    ):
        response = await receiveData(reader, passError=True)
        if response != b"\x00":
            writer.close()
            return
        serverDetails = orjson.dumps(
            {
                "version": {"name": self.config.detail.name, "protocol": 340},
                "players": {"max": self.config.server.max_players, "online": 0},
                "description": {"text": self.config.detail.motd},
            }
        )
        data = Data().addData(b"\x00").addDataWithLength(serverDetails)
        writer.write(data.getAllForSend())
        await writer.drain()
        response = await receiveData(reader, passError=True)
        if len(response) == 0:
            writer.close()
            return
        if response[0] != 1:
            writer.close()
            return
        data = Data(response)
        writer.write(data.getAllForSend())
        await writer.drain()
        writer.close()

    async def loginForGame(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        address: str,
        port: int,
        protocolVersion: int,
    ):
        response = Data(await receiveData(reader, passError=True))
        data = response.getData(1)
        if data != b"\x00":
            writer.close()
            return

        username = response.getString()
        verifyToken = os.urandom(4)
        serverId = (
            "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        ).encode("ascii")
        data = (
            Data()
            .addData(b"\x01")
            .addDataWithLength(serverId)
            .addDataWithLength(self.publicKey)
            .addDataWithLength(verifyToken)
        )
        writer.write(data.getAllForSend())
        await writer.drain()

        response = Data(await receiveData(reader, passError=True))
        if response.getData(1) != b"\x01":
            writer.close()
            return

        sharedSecret = self.key.decrypt(response.getBinary(), padding.PKCS1v15())
        clientVerifyToken = self.key.decrypt(response.getBinary(), padding.PKCS1v15())
        if verifyToken != clientVerifyToken:
            writer.close()
            return

        cipher = ciphers.Cipher(
            algorithms.AES(sharedSecret),
            modes.CFB8(sharedSecret),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()

        hash = hashlib.sha1()
        hash.update(serverId)
        hash.update(sharedSecret)
        hash.update(self.publicKey)
        hash = int(hash.hexdigest(), 16)
        if hash >> 156 & 8:
            hash = "-" + format(
                hash * -1 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, "x"
            )
        else:
            hash = format(hash, "x")
        # &ip={writer.get_extra_info('sockname')[0]}
        response = await self.http.get(
            f"https://sessionserver.mojang.com/session/minecraft/hasJoined?username={username}&serverId={hash}"
        )
        jsonData = response.json() if response.status_code == 200 else {}
        if response.status_code != 200 or "id" not in jsonData:
            kickMessage = orjson.dumps(
                {"text": "サーバーでの認証に失敗しました。", "color": "red"}
            )
            data = Data().addData(b"\x00").addDataWithLength(kickMessage)
            writer.write(data.getAllForSend(encryptor=encryptor))
            await writer.drain()
            writer.close()
            return

        """
        kickMessage = orjson.dumps(
            {"text": "HomuraMC Test Server / HomuraMCテストサーバー", "color": "green"}
        )
        data = Data().addData(b"\x00").addDataWithLength(kickMessage)
        writer.write(data.getAllForSend(encryptor=encryptor))
        await writer.drain()
        writer.close()
        return
        """

        # Compression packet
        if self.config.server.compression_threshold >= 0:
            data = (
                Data()
                .addData(b"\x03")
                .addData(encodeVarInt(self.config.server.compression_threshold))
            )

            writer.write(
                data.getAllForSend(
                    encryptor=encryptor,
                )
            )
            await writer.drain()

        data = (
            Data()
            .addData(b"\x02")
            .addDataWithLength(str(UUID(jsonData["id"])).encode())
            .addDataWithLength(jsonData["name"].encode())
        )

        writer.write(
            data.getAllForSend(
                encryptor=encryptor,
                compressionThreshold=self.config.server.compression_threshold,
            )
        )
        await writer.drain()

        player = Player(
            id=UUID(jsonData["id"]),
            name=jsonData["name"],
            encryptor=encryptor,
            decryptor=decryptor,
            writer=writer,
            reader=reader,
            entityId=random.randint(0, 10000),
        )
        await self.joinGame(player)

    async def sendChatMessage(self, message: dict, recipients: List[Player]):
        _message = orjson.dumps(message)
        for recipient in recipients:
            data = (
                Data()
                .addData(b"\x0f")
                .addDataWithLength(_message)
                .addData(struct.pack(">B", 0))
            )
            recipient.writer.write(
                data.getAllForSend(
                    encryptor=recipient.encryptor,
                    compressionThreshold=self.config.server.compression_threshold,
                )
            )
            await recipient.writer.drain()

    async def getPacket(self, player: Player):
        data = await receiveData(
            player.reader,
            passError=True,
            decryptor=player.decryptor,
            compressionThreshold=self.config.server.compression_threshold,
        )
        response = Data(data)
        if len(response.data) == 0:
            return
        packetId = response.getData(1)
        print(packetId, response.data)
        if packetId == b"\x0b":
            return
        elif packetId == b"\x02":
            message = response.getString()
            print(message)
            await self.sendChatMessage(
                {"text": f"<{player.name}> {message}"}, self.players
            )

    async def joinGame(self, player: Player):
        data = (
            Data()
            .addData(b"\x23")
            .addData(
                struct.pack(
                    ">iBiBB", player.entityId, 1, 0, 0, self.config.server.max_players
                )
            )
            .addDataWithLength("flat".encode())
            .addData(struct.pack(">?", False))
        )
        player.writer.write(
            data.getAllForSend(
                encryptor=player.encryptor,
                compressionThreshold=self.config.server.compression_threshold,
            )
        )
        await player.writer.drain()

        data = (
            Data()
            .addData(b"\x2f")
            .addData(struct.pack(">dddff?", 0, 255, 0, 0, 0, 0b00000))
            .addData(data.packVarInt(0))
        )
        player.writer.write(
            data.getAllForSend(
                encryptor=player.encryptor,
                compressionThreshold=self.config.server.compression_threshold,
            )
        )
        await player.writer.drain()

        data = (
            Data()
            .addData(b"\x2c")
            .addData(
                struct.pack(">?ff", 0b00000, 0.4000000059604645, 0.4000000059604645)
            )
        )
        player.writer.write(
            data.getAllForSend(
                encryptor=player.encryptor,
                compressionThreshold=self.config.server.compression_threshold,
            )
        )
        await player.writer.drain()

        self.players.append(player)
        try:
            await self.sendChatMessage(
                {
                    "text": f"{player.name} が世界に参加しました",
                    "color": "yellow",
                },
                self.players,
            )

            count = 0
            while not player.writer.is_closing():
                await self.getPacket(player)
                if count // 20:
                    data = Data().addData(b"\x1f").addData(struct.pack(">Q", 0))
                    player.writer.write(
                        data.getAllForSend(
                            encryptor=player.encryptor,
                            compressionThreshold=self.config.server.compression_threshold,
                        )
                    )
                    await player.writer.drain()
                count += 1
                await asyncio.sleep(0.05)
            self.players.remove(player)
        except ConnectionResetError:
            player.writer.close()
            self.players.remove(player)
