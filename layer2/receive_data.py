from typing import Callable, Generator
from bitstring import BitArray
from layer1 import manchester_encoding as me


def consume_bits_until_match(source: Generator[bool, None, None], pattern: BitArray):
    received_bits = []
    for bit in source:
        received_bits.append(bit)
        if pattern == received_bits[-len(pattern):]:
            return
        if len(received_bits) > 100000:
            break
    raise ValueError("Pattern not found")


def get_data_until_signal_dead(source: Generator[bool, None, None]) -> BitArray:
    return BitArray(auto=source)


def get_data_until_match(source: Generator[bool, None, None], pattern: BitArray) -> BitArray:
    received_bits = []
    for bit in source:
        received_bits.append(bit)
        if pattern == received_bits[-len(pattern):]:
            return BitArray(auto=received_bits[:-len(pattern)])
        if len(received_bits) > 100000:
            break
    raise ValueError("Pattern not found")


def decode_frame_bits(signal: Callable[[float], float], start_flag: BitArray, end_flag: BitArray = None) -> BitArray:
    decoded = me.decode(signal)
    consume_bits_until_match(decoded, start_flag)
    if end_flag is not None:
        return get_data_until_match(decoded, end_flag)
    else:
        return get_data_until_signal_dead(decoded)



