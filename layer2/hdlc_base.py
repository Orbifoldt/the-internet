import builtins
from abc import abstractmethod
from enum import Enum
from typing import Final

from bitstring import BitArray

from layer2.escape import EscapeSchema
from layer2.frame import Frame
from layer2.hdlc.control_field import ControlField
from layer2.tools import crc32, stuff_bit_array, destuff_bits, bits_to_bytes


class HdlcMode(Enum):
    NORMAL = 0
    ASYNC = 1
    ASYNC_BALANCED = 2


class HdlcLikeBaseFrame(Frame):
    flag: Final = b'\x7E'  # 01111110
    escape_byte: Final = b'\x7D'  # 01111101
    escape_schema: Final = EscapeSchema(b'\x7D', {b'\x7D': b'\x5D', b'\x7E': b'\x5E'})

    flag_bits = BitArray(auto=flag)
    bits_to_stuff: Final = [c == '1' for c in "11111"]
    stuffing_bit: Final = False

    @abstractmethod
    def __init__(self, address: int, control: ControlField, information: bytes = None, optional_field: bytes = None):
        if not (0 <= address < 2 ** 8):
            raise ValueError("Address must not be >= 0 and < 256")

        self.address = address
        self.control = control

        if information is None:
            self.information = bytes()
        else:
            self.information = information

        if optional_field is None:
            self.optional_field = bytes()
        else:
            self.optional_field = optional_field

        self.fcs = self.calculate_fcs()

    def calculate_fcs(self) -> bytes:
        all_data = self.address.to_bytes(1, 'big') + self.control.bytes + self.optional_field + self.information
        return crc32(all_data)

    def bytes(self) -> bytes:
        return self.address.to_bytes(1, 'big') + self.control.bytes + self.optional_field + self.information + self.fcs

    def encode_as_bytes(self, mode: HdlcMode) -> builtins.bytes:
        if mode == HdlcMode.NORMAL:
            raise ValueError(
                "Byte-encoding not supported for NORMAL mode: bit stuffing not compatible with byte format")
        return self.escape_schema.escape(self.bytes())

    def encode_as_bits(self, mode: HdlcMode) -> BitArray:
        if mode == HdlcMode.NORMAL:
            return stuff_bit_array(self.bits(), BitArray(auto=self.bits_to_stuff), self.stuffing_bit)
        else:
            return BitArray(auto=self.encode_as_bytes(mode))

    @classmethod
    def decode_from(cls, encoded: builtins.bytes | BitArray, **kwargs):
        mode: HdlcMode = kwargs['mode']

        if isinstance(encoded, bytes):
            if mode == HdlcMode.NORMAL:
                raise ValueError("Byte-encoding not supported for NORMAL mode: bit stuffing not compatible with byte "
                                 "format")
            return cls.decode_from_bytes(encoded)
        else:
            return cls.decode_from_bits(encoded, mode)

    @classmethod
    def decode_from_bytes(cls, encoded_bytes: bytes) -> builtins.bytes:
        return cls.escape_schema.unescape(encoded_bytes)

    @classmethod
    def decode_from_bits(cls, encoded_bits: BitArray, mode: HdlcMode) -> builtins.bytes:
        if mode == HdlcMode.NORMAL:
            destuffed = destuff_bits(list(encoded_bits), HdlcLikeBaseFrame.bits_to_stuff, HdlcLikeBaseFrame.stuffing_bit)
            if len(destuffed) % 8 != 0:
                raise ValueError(
                    f"Decoded frame contained {len(destuffed)} bits, multiple of 8 needed to read as bytes")
            return bits_to_bytes(destuffed)
        else:
            return cls.decode_from_bytes(bits_to_bytes(list(encoded_bits)))
