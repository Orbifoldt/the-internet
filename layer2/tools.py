import zlib


def crc32(data: bytes):
    return (zlib.crc32(data) & 0xFFFFFFFF).to_bytes(4, byteorder='little')
