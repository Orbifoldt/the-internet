from bitstring import BitArray

from layer2.ethernet.ethernet import EthernetFrame, EtherType
from layer2.ethernet.noneable_data_structures import NoneableBitArray, NoneableBytes
from layer2.mac import Mac
from layer2.tools import separate, crc32, bits_to_bytes


def decode(data: NoneableBitArray) -> list[EthernetFrame]:
    start_flag = BitArray(auto=EthernetFrame.preamble + EthernetFrame.start_frame_delim)
    bit_sections = separate(data, NoneableBitArray.from_bits(start_flag), [None] * EthernetFrame.inter_packet_gap_size)
    return [decode_frame(bits_to_bytes(frame_bytes)) for frame_bytes in bit_sections]


def decode_bytes(data: NoneableBytes) -> list[EthernetFrame]:
    start_flag = list(EthernetFrame.preamble + EthernetFrame.start_frame_delim)
    end_flag = NoneableBytes.nones(int(EthernetFrame.inter_packet_gap_size / 8))
    separated_sections = separate(data, start_flag, end_flag)
    byte_sections = [bytes([0 if x is None else x for x in frame_bytes]) for frame_bytes in separated_sections]
    return [decode_frame(byte_section) for byte_section in byte_sections]


def decode_frame(frame_bytes: bytes) -> EthernetFrame:
    """
    Create an EthernetFrame from the provided bytes, or throw an ValueError if the bytes are corrupted
    """
    mac_dest = Mac(frame_bytes[0:6])
    mac_src = Mac(frame_bytes[6:12])
    ether_type = EtherType(int.from_bytes(frame_bytes[12:14], byteorder='big'))
    payload = frame_bytes[14:-4]
    fcs = frame_bytes[-4:]

    calculated_fcs = crc32(frame_bytes[:-4])
    if fcs != calculated_fcs:
        raise ValueError(f"The calculated FCS '{calculated_fcs}' does not equal FCS of the received frame: '{fcs}'",
                         mac_dest, mac_src, ether_type, frame_bytes)

    return EthernetFrame(mac_dest, mac_src, payload, ether_type)
