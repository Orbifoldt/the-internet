from typing import Callable

from bitstring import BitArray

from layer2.mac import Mac
from layer2.receive_data import decode_frame_bits
from ethernet import EthernetFrame, EtherType
from layer2.tools import crc32


def ethernet_frame_from(signal: Callable[[float], float]) -> EthernetFrame:
    start_flag = EthernetFrame.preamble + EthernetFrame.start_frame_delim
    frame_bytes = decode_frame_bits(signal, BitArray(auto=start_flag), end_flag=None).bytes

    mac_dest = Mac(frame_bytes[0:6])
    mac_src = Mac(frame_bytes[6:12])
    ether_type = EtherType(int.from_bytes(frame_bytes[12:14], byteorder='big'))
    payload = frame_bytes[14:-4]
    fcs = frame_bytes[-4:]

    calculated_fcs = crc32(frame_bytes[:-4])
    if fcs != calculated_fcs:
        raise ValueError(f"The calculated FCS '{calculated_fcs}' does not equal FCS of the received frame: '{fcs}'")

    return EthernetFrame(mac_dest, mac_src, payload, ether_type)

