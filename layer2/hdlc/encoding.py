from bitstring import BitArray

from layer2.hdlc.hdlc import HdlcFrameBase, HdlcMode
from layer2.tools import interleave, reduce_bits, reduce_bytes


def encode(frames: list[HdlcFrameBase], mode: HdlcMode) -> BitArray:
    encoded_frames = [frame.encode_as_bits(mode) for frame in frames]
    marked_frame_boundaries = interleave(encoded_frames, HdlcFrameBase.flag_bits)
    return reduce_bits(marked_frame_boundaries)


def encode_bytes(frames: list[HdlcFrameBase], mode: HdlcMode) -> bytes:
    if mode == HdlcMode.NORMAL:
        raise ValueError("Byte-encoding not supported for NORMAL mode: bit stuffing not compatible with byte format")

    encoded_frames = [frame.encode_as_bytes() for frame in frames]
    marked_frame_boundaries = interleave(encoded_frames, HdlcFrameBase.flag)
    return reduce_bytes(marked_frame_boundaries)
