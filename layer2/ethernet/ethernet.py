from enum import Enum
from typing import Final

from bitstring import BitArray
from layer2.mac import Mac
from layer2.tools import crc32


class EtherType(Enum):
    IPV4 = 0x0800
    IPV6 = 0x86DD
    ARP = 0x0806

    def to_bytes(self):
        return self.value.to_bytes(2, byteorder="big")


# TODO: refactor to extract common functionality from this and the 802.3 frame
class EthernetFrame:
    preamble: Final = int("10" * 28, 2).to_bytes(7, byteorder="big")
    start_frame_delim: Final = int("10101011", 2).to_bytes(1, byteorder="big")
    inter_packet_gap_size: Final = 96

    MIN_PAYLOAD = 46
    MAX_PAYLOAD = 1500

    def __init__(self, destination: Mac, source: Mac, payload: bytes, ether_type: EtherType = EtherType.IPV4) -> None:
        if ether_type != EtherType.IPV4:
            raise ValueError("This ether type is not yet implemented")
        if len(payload) > self.MAX_PAYLOAD:
            raise ValueError(f"Max payload size si {self.MAX_PAYLOAD} bytes, received {len(payload)} bytes.")
        if len(payload) < self.MIN_PAYLOAD:
            payload += bytearray(self.MIN_PAYLOAD - len(payload))

        self.destination = destination
        self.source = source
        self.ether_type = ether_type
        self.payload = payload
        self.fcs = self.calculate_fcs()

    def calculate_fcs(self):
        all_data = self.destination.address + self.source.address + self.ether_type.to_bytes() + self.payload
        return crc32(all_data)

    def bytes(self):
        return self.destination.address + self.source.address + self.ether_type.to_bytes() + self.payload + self.fcs

    def phys_bytes(self):
        return self.preamble + self.start_frame_delim + self.bytes()

    def bits(self):
        return BitArray(auto=self.bytes())

    def phys_bits(self):
        return BitArray(auto=self.phys_bytes())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.bytes() == self.bytes()


class LlcType(Enum):  # IEEE 802.1Q
    DEFAULT = 0x81000000  # Last 4 hex digits (i.e. last 2 bytes) contain Tag Control Information (not implemented here)

    def to_bytes(self):
        return self.value.to_bytes(4, byteorder="big")

    def get_tpid(self):
        return self.to_bytes()[2:]

    def get_tci(self):
        return self.to_bytes()[-2:]


class Ethernet802_3Frame:
    preamble: Final = int("10" * 28, 2).to_bytes(7, byteorder="big")
    start_frame_delim: Final = int("10101011", 2).to_bytes(1, byteorder="big")
    inter_packet_gap_size: Final = 96

    MIN_PAYLOAD: Final = 42
    MAX_PAYLOAD: Final = 1500

    def __init__(self, destination: Mac, source: Mac, payload: bytes, llc_type: LlcType = LlcType.DEFAULT) -> None:
        if llc_type != LlcType.DEFAULT:
            raise ValueError("This LLC type is not yet implemented")
        if len(payload) > self.MAX_PAYLOAD:
            raise ValueError(f"Max payload size si {self.MAX_PAYLOAD} bytes, received {len(payload)} bytes.")

        self.size = len(payload).to_bytes(2, byteorder='big')
        if len(payload) < self.MIN_PAYLOAD:
            payload += bytearray(self.MIN_PAYLOAD - len(payload))

        self.destination = destination
        self.source = source
        self.llc_type = llc_type
        self.payload = payload
        self.fcs = self.calculate_fcs()

    def calculate_fcs(self):
        all_data = self.destination.address + self.source.address + self.size \
                   + self.llc_type.to_bytes() + self.payload
        return crc32(all_data)

    def bytes(self):
        return self.destination.address + self.source.address + self.size + self.llc_type.to_bytes() + self.payload \
               + self.fcs

    def phys_bytes(self):
        return self.preamble + self.start_frame_delim + self.bytes()

    def bits(self):
        return BitArray(auto=self.bytes())

    def phys_bits(self):
        return BitArray(auto=self.phys_bytes())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.bytes() == self.bytes()
