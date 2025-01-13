import asyncio


def encodeVarInt(num):
    res = b""
    while num:
        b = num & 127
        num = num >> 7
        if num != 0:
            b |= 128
        res += bytes([b])
    return res


def decodeVarInt(data):
    val = 0
    shift = 0
    for d in data:
        val |= (d & 127) << shift
        if not (d & 128):
            break
        shift += 7
    return val


async def receiveData(reader: asyncio.StreamReader, *, passError: bool = False):
    buffer = b""
    while True:
        r = await reader.read(1)
        buffer += r
        try:
            if not r[0] & 128:
                break
        except IndexError as e:
            if passError:
                break
            else:
                raise e
    size = decodeVarInt(buffer)
    return await reader.read(size)
