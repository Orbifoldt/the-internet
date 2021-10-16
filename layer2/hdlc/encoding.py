from bitstring import BitArray

from layer2.hdlc.hdlc import HdlcFrameBase, HdlcMode
from layer2.tools import interleave


def encode(frames: list[HdlcFrameBase], mode: HdlcMode) -> BitArray:
    encoded_frames = [frame.encode_as_bits(mode) for frame in frames]
    concatenated_bits = BitArray()
    for section in interleave(encoded_frames, HdlcFrameBase.flag_bits):
        concatenated_bits += section
    return concatenated_bits


def encode_bytes(frames: list[HdlcFrameBase], mode: HdlcMode) -> bytes:
    if mode == HdlcMode.NORMAL:
        raise ValueError("Byte-encoding not supported for NORMAL mode: bit stuffing not compatible with byte format")

    encoded_frames = [frame.encode_as_bytes() for frame in frames]
    concatenated_bytes = bytes()
    for section in interleave(encoded_frames, HdlcFrameBase.flag):
        concatenated_bytes += section
    return concatenated_bytes