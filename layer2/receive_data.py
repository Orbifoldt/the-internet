from typing import Callable
from bitstring import BitArray
from layer1 import manchester_encoding as me


def decode_to_bits(signal: Callable[[float], float], start_flag: BitArray, end_flag: BitArray):
    decoded = me.decode(signal)
    received_bits = []
    count = 0

    start_bits = [b for b in start_flag]
    while True:
        received_bits.append(next(decoded))
        count += 1
        if count >= len(start_flag):
            if start_bits == received_bits[-len(start_flag):]:
                break
        if count >= 10000:
            raise ValueError("no match for start found in signal")

    data = []
    end_bits = [b for b in end_flag]
    while True:
        bit = next(decoded)
        count += 1
        data.append(bit)
        received_bits.append(bit)

        if count >= len(end_flag):
            if end_bits == received_bits[-len(end_flag):]:
                break
        if count >= 20000:
            raise ValueError("no match for start found in signal")
    data = data[:-len(end_flag)]
    return BitArray(auto=data)



