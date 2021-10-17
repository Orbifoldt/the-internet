from bitstring import BitArray


class NoneableBitArray(list[bool | None]):
    @staticmethod
    def from_bits(bits: BitArray):
        return NoneableBitArray() + [b for b in bits]

    @staticmethod
    def nones(n: int):
        return NoneableBitArray() + [None] * n


class NoneableBytes(list[int | None]):
    @staticmethod
    def from_bytes(byte_data: bytes):
        return NoneableBytes() + [x for x in byte_data]

    @staticmethod
    def nones(n: int):
        return NoneableBytes() + [None] * n