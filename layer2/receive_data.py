from typing import Callable, Generator, TypeVar
from bitstring import BitArray
from layer1 import manchester_encoding as me
from layer2.tools import bit_to_byte_generator

T = TypeVar('T')


def consume_elements_until_match(source: Generator[T, None, None], pattern: list[T]) -> None:
    received = []
    for element in source:
        received.append(element)

        if pattern_matches(received, pattern):
            return

        if len(received) > 100000:
            raise ValueError("Pattern not found")


def get_data_until_match(source: Generator[T, None, None], pattern: list[T], escape: list[T] = None) -> list[T]:
    received = []
    for elt in source:
        received.append(elt)

        if pattern_matches(received, pattern):
            if escape is not None and pattern_matches(received, escape + pattern):
                del received[-len(pattern) - len(escape):-len(pattern)]
                continue
            return received[:-len(pattern)]

        if len(received) > 100000:
            raise ValueError("Pattern not found")


def pattern_matches(data: list[T], pattern: list[T]) -> bool:
    return pattern == data[-len(pattern):]


def get_data_bits_until_signal_dead(source: Generator[bool, None, None]) -> BitArray:
    return BitArray(auto=source)


def get_data_bytes_until_signal_dead(source: Generator[int, None, None]) -> bytes:
    return bytes(source)


def decode_frame_bits(signal: Callable[[float], float], start_flag: BitArray,
                      end_flag: BitArray = None, escape: BitArray = None) -> BitArray:
    decoded = me.decode(signal)
    consume_elements_until_match(decoded, pattern=list(start_flag))

    if end_flag is not None:
        data = get_data_until_match(decoded, list(end_flag), escape)
        return BitArray(auto=data)
    else:
        return get_data_bits_until_signal_dead(decoded)


def decode_frame_bytes(signal: Callable[[float], float], start_flag: bytes,
                       end_flag: bytes = None, escape: bytes = None) -> bytes:
    decoded = me.decode(signal)
    consume_elements_until_match(decoded, list(BitArray(auto=start_flag)))

    byte_source = bit_to_byte_generator(source=decoded)
    if end_flag is not None:
        if escape is not None:
            escape = list(escape)
        data = get_data_until_match(byte_source, list(end_flag), escape)
        return bytes(data)
    else:
        return get_data_bytes_until_signal_dead(byte_source)
