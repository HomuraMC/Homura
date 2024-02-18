import asyncio
import json
import struct
from Crypto.PublicKey import RSA
import logger
import os

log = logger.get_module_logger(__name__, verbose=True)

log.info("Loading libraries. please wait...")

# 1024ビットのRSAキーペアを生成
key = RSA.generate(1024)

# 公開鍵を表示 しません
# log.info(key.publickey().export_key())

# 秘密鍵を表示 しません
# log.info(key.export_key())

def pack_varint(data: int) -> bytes:
	o = b''

	while True:
		byte = data & 0x7F
		data >>= 7
		o += struct.pack('B', byte | (0x80 if data > 0 else 0))

		if data == 0:
			break

	return o

async def unpack_varint_socket(reader: asyncio.StreamReader) -> int:
	data = 0
	for i in range(5):
		byte = await reader.readexactly(1)
		if not byte:
			break

		byte = ord(byte)
		data |= (byte & 0x7F) << 7 * i

		if not byte & 0x80:
			break

	return data

async def send_data(writer: asyncio.StreamWriter, response):
	writer.write(response)
	await writer.drain()

async def read_long_data(reader: asyncio.StreamReader, size: int) -> bytearray:
	data = bytearray()

	while len(data) < size:
		chunk = await reader.readexactly(size - len(data))
		data += bytearray(chunk)

	return data

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
	packet_len = await unpack_varint_socket(reader)
	data = await read_long_data(reader, packet_len)

	log.info(reader)
	log.info(data)

	if data[-1] == 1:
		await status(writer)
	elif data[-1] == 2:
		await login(writer)

async def status(writer: asyncio.StreamWriter):
	status_data = {
		"version": {
			"name": "1.16.5",
			"protocol": 754
		},
		"players": {
			"max": 0,
			"online": 0
		},
		"description": {
			"text": "せつめい"
		}
	}
	response = json.dumps(status_data).encode('utf8')
	response = pack_varint(len(response)) + response
	response = pack_varint(0x00) + response
	response = pack_varint(len(response)) + response
	await send_data(writer, response)

def generate_verify_token():
    # Generate a 4-byte random token
    verify_token = os.urandom(4)
    return verify_token

async def login(writer: asyncio.StreamWriter):
	response = pack_varint(len("")) + "".encode('utf8')
	response = response + pack_varint(len(key.publickey().export_key())) + key.publickey().export_key()
	response = response + pack_varint(4) + generate_verify_token()
	response = pack_varint(0x01) + response
	response = pack_varint(len(response)) + response
	await send_data(writer, response)

async def main():
	server = await asyncio.start_server(handle_client, '127.0.0.1', 25565)

	async with server:
		try:
			log.info("Server Listened at 127.0.0.1:25565")
			await server.serve_forever()
		except KeyboardInterrupt:
			pass
		finally:
			server.close()

if __name__ == "__main__":
	asyncio.run(main())
