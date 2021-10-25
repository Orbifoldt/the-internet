from typing import List

from bitstring import BitArray


def int_to_bits(n: int) -> List[int]:
    bits = []
    remainder = n
    while True:
        bit_i = remainder & 1
        bits.append(bit_i)
        remainder = remainder >> 1
        if remainder == 0:
            break
    return bits


def bits_to_int(bits: List[int]) -> int:
    x = 0
    for bit in reversed(bits):
        x = (x << 1) | bit
    return x


def checksum(bits: BitArray) -> BitArray:
    chk = 0
    for i in range(0, len(bits), 16):
        a = int(bits[i: i + 8].bin, 2)
        b = int(bits[i + 8: i + 16].bin, 2) << 8
        c = chk + a + b
        chk = (c & 0xffff) + (c >> 16)
    chk = ~chk & 0xffff
    chk_bits = BitArray(uint=chk, length=16)
    return chk_bits[8:] + chk_bits[:8]  # switch around the order
