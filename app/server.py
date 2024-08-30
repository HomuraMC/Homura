import asyncio
import hashlib
import logging
import os
import random
import string
import struct

import aiohttp
import orjson
from nbt import nbt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import ciphers, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from .config import Config
from .objects import Player
from .utils import Utils


class Server:
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=1024, backend=default_backend()
    )
    publicKey = key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    logger = logging.getLogger("HomuraMC")
    config = Config().config

    @classmethod
    async def serverLoop(
        cls, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        # varint
        buffer = b""
        while True:
            r = await reader.read(1)
            buffer += r
            if not r[0] & 128:
                break
        size = Utils.decodeVarInt(buffer)
        response = await reader.read(size)

        # get packet id
        received = b""
        position = 0
        for r in response:
            received += bytes([r])
            position += 1
            if not r & 128:
                break
        packet_id = Utils.decodeVarInt(received)
        if packet_id != 0:
            writer.close()
            return

        # get protocol version
        received = b""
        for r in response[position:]:
            received += bytes([r])
            position += 1
            if not r & 128:
                break
        protocolVersion = Utils.decodeVarInt(received)

        # get address and port
        received = b""
        for r in response[position:]:
            received += bytes([r])
            position += 1
            if not r & 128:
                break
        size = Utils.decodeVarInt(received)
        address = response[position : position + size].decode("utf-8")
        position += size
        port = struct.unpack(">H", response[position : position + 2])[0]
        position += 2
        received = b""
        for r in response[position:]:
            received += bytes([r])
            position += 1
            if not r & 128:
                break
        nextState = Utils.decodeVarInt(received)

        if nextState == 1:
            await cls.sendServerDetails(
                reader, writer, protocolVersion, address, port, nextState
            )
        elif nextState == 2:
            await cls.login(reader, writer, protocolVersion, address, port, nextState)
        else:
            writer.close()
            return

    @classmethod
    async def sendServerDetails(
        cls,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        protocolVersion: int,
        address: str,
        port: int,
        nextState: int,
    ):
        response = b""
        while True:
            r = await reader.read(1)
            response += r
            try:
                if not r[0] & 128:
                    break
            except IndexError:
                break
        size = Utils.decodeVarInt(response)
        response = await reader.read(size)
        if response != b"\x00":
            writer.close()
            return
        data = orjson.dumps(
            {
                "version": {"name": "Homura", "protocol": 754},
                "players": {"max": cls.config.server.max_players, "online": 0},
                "description": {"text": cls.config.detail.motd},
            }
        )
        data = b"\x00" + Utils.encodeVarInt(len(data)) + data
        writer.write(Utils.encodeVarInt(len(data)) + data)
        await writer.drain()
        pos = 0
        response = b""
        while True:
            r = await reader.read(1)
            response += r
            pos += 1
            try:
                if not r[0] & 128:
                    break
            except IndexError:
                break
        size = Utils.decodeVarInt(response)
        response = await reader.read(size)
        if len(response) == 0:
            writer.close()
            return
        if response[0] != 1:
            writer.close()
            return
        data = response
        data = Utils.encodeVarInt(len(data)) + data
        writer.write(data)
        await writer.drain()
        writer.close()

    @classmethod
    async def login(
        cls,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        protocolVersion: int,
        address: str,
        port: int,
        nextState: int,
    ):
        responst = b""
        while True:
            r = await reader.read(1)
            responst += r
            if not r[0] & 128:
                break
        size = Utils.decodeVarInt(responst)
        responst = await reader.read(size)
        position = 0
        if responst[0] != 0:
            writer.close()
            return
        position += 1
        received = b""
        for r in responst[position:]:
            received += bytes([r])
            position += 1
            if not r & 128:
                break
        size = Utils.decodeVarInt(received)
        username = responst[position : position + size].decode("utf-8")
        verifyToken = os.urandom(4)
        serverId = (
            "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        ).encode("ascii")
        data = (
            b"\x01"
            + Utils.encodeVarInt(len(serverId))
            + serverId
            + Utils.encodeVarInt(len(cls.publicKey))
            + cls.publicKey
            + Utils.encodeVarInt(len(verifyToken))
            + verifyToken
        )
        data = Utils.encodeVarInt(len(data)) + data
        writer.write(data)
        await writer.drain()

        response = b""
        while True:
            r = await reader.read(1)
            response += r
            if not r[0] & 128:
                break
        size = Utils.decodeVarInt(response)
        response = await reader.read(size)
        if response[0] != 1:
            writer.close()
            return
        position = 1
        received = b""
        for r in response[position:]:
            received += bytes([r])
            position += 1
            if not r & 128:
                break
        size = Utils.decodeVarInt(received)
        sharedSecret = response[position : position + size]
        sharedSecret = cls.key.decrypt(sharedSecret, padding.PKCS1v15())
        position += size
        received = b""
        for r in response[position:]:
            position += 1
            if len(received) == 0 and r == 0:
                continue
            received += bytes([r])
            if not r & 128:
                break
        size = Utils.decodeVarInt(received)
        clientVerifyToken = response[position : position + size]
        clientVerifyToken = cls.key.decrypt(clientVerifyToken, padding.PKCS1v15())
        if verifyToken != verifyToken:
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
        hash.update(cls.publicKey)
        hash = int(hash.hexdigest(), 16)
        if hash >> 156 & 8:
            hash = "-" + format(
                hash * -1 & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, "x"
            )
        else:
            hash = format(hash, "x")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://sessionserver.mojang.com/session/minecraft/hasJoined?username={username}&serverId={hash}"
            ) as hasJoined:
                hasJoinedResponse: dict = (
                    await hasJoined.json() if hasJoined.status == 200 else {}
                )
                if hasJoined.status != 200 or "id" not in hasJoinedResponse:
                    data = orjson.dumps(
                        {"text": "サーバーでの認証に失敗しました。", "color": "red"}
                    )
                    data = b"\x00" + Utils.encodeVarInt(len(data)) + data
                    data = Utils.encodeVarInt(len(data)) + data
                    data = encryptor.update(data)
                    writer.write(data)
                    await writer.drain()
                    writer.close()
                    return

        hasJoinedResponse["protocolVersion"] = protocolVersion
        hasJoinedResponse["reader"] = reader
        hasJoinedResponse["writer"] = writer
        player: Player = Player.model_validate(hasJoinedResponse)
        cls.logger.info(f"{player.name} is trying connect...")

        data = Utils.encodeVarInt(cls.config.server.compression_threshold)
        data = b"\x03" + Utils.encodeVarInt(len(data)) + data
        writer.write(Utils.encodeVarInt(len(data)) + data)
        await writer.drain()

        data = player.id.bytes + Utils.packString(player.name)
        data = b"\x02" + Utils.encodeVarInt(len(data)) + data
        data = Utils.packPacket(data, cls.config.server.compression_threshold)
        writer.write(data)
        await writer.drain()

        dimensionCodec = nbt.NBTFile()

        dimensionTypes = nbt.TAG_Compound(name="minecraft:dimension_type")
        dimensionTypes.tags.append(
            nbt.TAG_String(name="type", value="minecraft:dimension_type")
        )

        registries = nbt.TAG_List(name="value")
        registries.tags.append(nbt.TAG_String(name="name", value="minecraft:overworld"))
        registries.tags.append(nbt.TAG_Int(name="id", value=0))

        elements = nbt.TAG_Compound()
        elements.tags.append(nbt.TAG_Byte(name="natural", value=1))
        elements.tags.append(nbt.TAG_Float(name="ambient_light", value=0.0))
        elements.tags.append(
            nbt.TAG_String(name="infiniburn", value="minecraft:infiniburn_overworld")
        )
        elements.tags.append(nbt.TAG_Byte(name="respawn_anchor_works", value=0))
        elements.tags.append(nbt.TAG_Byte(name="has_skylight", value=1))
        elements.tags.append(nbt.TAG_Byte(name="bed_works", value=1))
        elements.tags.append(
            nbt.TAG_String(name="effects", value="minecraft:overworld")
        )
        elements.tags.append(nbt.TAG_Byte(name="has_raids", value=1))
        elements.tags.append(nbt.TAG_Int(name="logical_height", value=256))
        elements.tags.append(nbt.TAG_Float(name="coordinate_scale", value=1.0))
        elements.tags.append(nbt.TAG_Byte(name="ultrawarm", value=0))
        elements.tags.append(nbt.TAG_Byte(name="has_ceiling", value=0))

        data = (
            struct.pack(">i?BB", 0, False, 1, 1)
            + Utils.packVarInt(1)
            + Utils.packString("overworld")
            + b"\x00"
            + b"\x00"
            + Utils.packString("overworld")
            + struct.pack(">q", 42)
            + Utils.packVarInt(0)
            + Utils.packVarInt(2)
            + struct.pack(">????", False, True, False, False)
        )
        data = b"\x24" + Utils.encodeVarInt(len(data)) + data
        data = Utils.packPacket(data, cls.config.server.compression_threshold)
        writer.write(data)
        await writer.drain()

        data = struct.pack(">dddff?", 8, 63, 8, 0, 90, 0b00000) + Utils.packVarInt(0)
        data = b"\x34" + Utils.encodeVarInt(len(data)) + data
        data = Utils.packPacket(data, cls.config.server.compression_threshold)
        writer.write(data)
        await writer.drain()

        cls.logger.info(f"{player.name} joined the game")
        await cls.tickLoop(player)

    @classmethod
    async def tickLoop(cls, player: Player):
        count = 0
        while True:
            data = struct.pack(">Q", 0)
            data = b"\x1F" + Utils.encodeVarInt(len(data)) + data
            data = Utils.packPacket(data, cls.config.server.compression_threshold)
            player.writer.write(data)
            await player.writer.drain()
            count += 1
            await asyncio.sleep(0.05)
