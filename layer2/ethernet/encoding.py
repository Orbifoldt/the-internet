from layer2.ethernet.ethernet import EthernetFrame
from layer2.ethernet.noneable_data_structures import NoneableBitArray, NoneableBytes
from layer2.tools import interleave, reduce


def encode(frames: list[EthernetFrame]) -> NoneableBitArray:
    encoded_frames = [NoneableBitArray.from_bits(frame.phys_bits()) for frame in frames]
    marked_frame_boundaries = interleave(encoded_frames, NoneableBitArray.nones(EthernetFrame.inter_packet_gap_size))
    return reduce(marked_frame_boundaries, NoneableBitArray(), lambda a, b: a + b)


def encode_bytes(frames: list[EthernetFrame]) -> NoneableBytes:
    encoded_frames = [NoneableBytes.from_bytes(frame.phys_bytes()) for frame in frames]
    sep = NoneableBytes.nones(int(EthernetFrame.inter_packet_gap_size / 8))
    marked_frame_boundaries = interleave(encoded_frames, sep)
    return reduce(marked_frame_boundaries, NoneableBytes(), lambda a, b: a + b)
