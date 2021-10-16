import zlib
from typing import Iterable, Generator, TypeVar, Optional, Tuple

from bitstring import BitArray

T = TypeVar('T')


#####################################
#         Checksums/hashes          #
#####################################


def crc32(data: bytes) -> bytes:
    return (zlib.crc32(data) & 0xFFFFFFFF).to_bytes(4, byteorder='little')


#####################################
#     Bits <-> Bytes conversions    #
#####################################


def bits_to_int(bits: Iterable[bool]) -> int:
    byte = 0
    for b in bits:
        byte = (byte << 1) | b
    return byte


def chunks(data: list[T], chunk_size: int):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


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


#####################################
#        list manipulations         #
#####################################


def find_match(data: list[T], pattern: list[T], start_idx: int = 0, escape: list[T] = None) -> Optional[int]:
    """
    Find the first match of a pattern as a sublist inside the data after the start_idx. Will ignore any occurrences of
    the pattern which are preceded by the escape (if not None). Returns None if no match is found.
    """
    if len(pattern) + start_idx > len(data) or len(pattern) == 0:
        return None
    escape_length = len(escape) if escape is not None else 0

    for i in range(start_idx, len(data) - len(pattern) + 1):
        data_slice = data[i - escape_length:i + len(pattern)]
        if pattern_matches_end(data_slice, pattern):
            if (escape is None) or not pattern_matches_end(data_slice, escape + pattern):
                return i
    return None


def pattern_matches_end(data: list[T], pattern: list[T]) -> bool:
    return pattern == data[-len(pattern):]


def replace_all_matches(data: list[T], pattern: list[T], replacement: list[T], escape: list[T] = None) -> list[T]:
    """
    Replace all occurrences of the pattern as a sublist inside the data with a given replacement sublist. Ignores any
    occurrences of the pattern that are preceded by the escape pattern (it not None)
    """
    i = 0
    while (i := find_match(data, pattern, i, escape)) is not None:
        data[i:i + len(pattern)] = replacement
        i += len(replacement)
    return data


def interleave(elts: list[T], sep: T) -> list[T]:
    return [sep] + [val for elt in elts for val in (elt, sep)]


def get_data_between_flags(data: list[T], start_flag: list[T], end_flag: list[T]) -> Tuple[list[T], int, int]:
    if (start_idx := find_match(data, start_flag, 0)) is None:
        raise ValueError("Pattern start_flag not found")
    if (end_idx := find_match(data, end_flag, start_idx + len(start_flag))) is None:
        raise ValueError("Pattern end_flag not found")
    return data[start_idx + len(start_flag): end_idx], start_idx, end_idx


def separate(data: list[T], start_flag: list[T], end_flag: list[T] = None) -> list[list[T]]:
    """
    Get a list of all sublists of data which are preceded by start_flag and succeeded by end_flag. If end_flag is
    omitted, then the start_flag is also used as final delimiter. The end_flag of one block may overlap with the
    start_flag of the next block.

    Examples:
    start_flag = A, end_flag = B
        A + X + B -> [X]
        X0 + A + X1 + B + X2 + A + X3 + B + X4 -> [X1, X3]
        A + X0 + A + X1 + B -> [X0 + A + X1]  (i.e. a list with a list as its single element)
        A + X0 + B + X1 + B -> [X0]
    start_flag = A, end_flag = None (or, equivalently, end_flag = A)
        A + X + A -> [X]
        A + X0 + A + X1 + A -> [X0, X1]
    """
    if end_flag is None:
        end_flag = start_flag
    separated_blocks = []
    remaining_data = data
    while True:
        try:
            data_block, _, end_idx = get_data_between_flags(remaining_data, start_flag, end_flag)
            separated_blocks.append(data_block)
            remaining_data = remaining_data[end_idx:]
        except ValueError:
            break
    return separated_blocks


#####################################
#      Stuffing and undoing it      #
#####################################


def stuff_bits(data: list[bool], pattern: list[bool], stuffing_bit: bool) -> list[bool]:
    return replace_all_matches(data, pattern, pattern + [stuffing_bit])


def stuff_bit_array(data: BitArray, pattern: BitArray, stuffing_bit: bool) -> BitArray:
    return BitArray(auto=stuff_bits(list(data), list(pattern), stuffing_bit))


def destuff_bits(stuffed_data: list[bool], pattern: list[bool], stuffing_bit: bool) -> list[bool]:
    return replace_all_matches(stuffed_data, pattern + [stuffing_bit], pattern)