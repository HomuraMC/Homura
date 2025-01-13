import asyncio
import logging

import os
import orjson
import random
import string
import hashlib
from httpx import AsyncClient
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import ciphers, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from .config import Config
from .objects.data import Data
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
                "version": {"name": "Homura", "protocol": 340},
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
        data = Data()
        data.addDataWithLength(response)
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

        kickMessage = orjson.dumps(
            {"text": "HomuraMC Test Server / HomuraMCテストサーバー", "color": "green"}
        )
        data = Data().addData(b"\x00").addDataWithLength(kickMessage)
        writer.write(data.getAllForSend(encryptor=encryptor))
        await writer.drain()
        writer.close()
        return
