import zlib
from typing import Iterable, Generator, TypeVar, Optional

from bitstring import BitArray

T = TypeVar('T')


def crc32(data: bytes) -> bytes:
    return (zlib.crc32(data) & 0xFFFFFFFF).to_bytes(4, byteorder='little')


def bits_to_int(bits: Iterable[bool]) -> int:
    byte = 0
    for b in bits:
        byte = (byte << 1) | b
    return byte


def chunks(data: list[T], n: int):
    for i in range(0, len(data), n):
        yield data[i:i + n]


def bits_to_bytes(bits: list[bool]):
    return bytes([bits_to_int(chunk) for chunk in chunks(bits, 8)])


def bit_to_byte_generator(source: Generator[bool, None, None]) -> Generator[int, None, None]:
    source_alive = True
    while source_alive:
        bits = [False] * 8
        for i in range(8):
            try:
                bit = next(source)
                bits[i] = bit
            except StopIteration:
                source_alive = False
                break
        byte = bits_to_int(bits)
        yield byte


def find_match(data: list[T], sub_list: list[T], start_index: int = 0) -> Optional[int]:
    n = len(data)
    if len(sub_list) + start_index > n or len(sub_list) == 0:
        return None
    for i in range(start_index, n - len(sub_list) + 1):
        if data[i:i + len(sub_list)] == sub_list:
            return i


def replace_all_matches(data: list[T], pattern: list[T], replacement: list[T]) -> list[T]:
    i = 0
    while (i := find_match(data, pattern, i)) is not None:
        data[i:i + len(pattern)] = replacement
        i += len(replacement)
    return data


def stuff_bits(data: list[bool], pattern: list[bool], stuffing_bit: bool) -> list[bool]:
    return replace_all_matches(data, pattern, pattern + [stuffing_bit])


def destuff_bits(data: list[bool], stuffed_pattern: list[bool]) -> list[bool]:
    return replace_all_matches(data, stuffed_pattern, stuffed_pattern[:-1])


def interleave(elts: list[T], sep: T) -> list[T]:
    return [sep] + [val for elt in elts for val in (elt, sep)]


def encode_with_flag(frames: list[bytes], sep: bytes) -> bytes:
    combined = bytes()
    for section in interleave(frames, sep):
        combined += section
    return combined
