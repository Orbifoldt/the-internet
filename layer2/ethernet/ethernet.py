import zlib
from enum import Enum
from bitstring import BitArray
from layer2.mac import Mac


def crc32(data: bytes):
    return (zlib.crc32(data) & 0xFFFFFFFF).to_bytes(4, byteorder='little')


class EtherType(Enum):
    IPV4 = 0x0800
    IPV6 = 0x86DD
    ARP = 0x0806

    def to_bytes(self):
        return self.value.to_bytes(2, byteorder="big")


class EthernetFrame:
    preamble = int("10" * 28, 2).to_bytes(7, byteorder="big")
    start_frame_delim = int("10101011", 2).to_bytes(1, byteorder="big")
    inter_packet_gap = 0b0.to_bytes(12, byteorder="big")

    def __init__(self, destination: Mac, source: Mac, payload: bytes, ether_type: EtherType = EtherType.IPV4) -> None:
        super().__init__()
        if ether_type != EtherType.IPV4:
            raise ValueError("This ether type is not yet implemented")
        if len(payload) > 1500:
            raise ValueError(f"The payload may not contain more than 1500 bytes, received {len(payload)} bytes.")
        if len(payload) < 46:
            payload = payload.zfill(46)

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

    def to_bits(self):
        return BitArray(bin=bin(int.from_bytes(self.bytes(), byteorder="big")))


class LlcType(Enum):  # IEEE 802.1Q
    DEFAULT = 0x81000000  # Last 4 hex digits (i.e. last 2 bytes) contain Tag Control Information (not implemented here)

    def to_bytes(self):
        return self.value.to_bytes(4, byteorder="big")

    def get_tpid(self):
        return self.to_bytes()[2:]

    def get_tci(self):
        return self.to_bytes()[-2:]


class Ethernet802_3Frame:
    preamble = int("10" * 28, 2).to_bytes(7, byteorder="big")
    start_frame_delim = int("10101011", 2).to_bytes(1, byteorder="big")
    inter_packet_gap = 0b0.to_bytes(12, byteorder="big")

    def __init__(self, destination: Mac, source: Mac, payload: bytes, llc_type: LlcType = LlcType.DEFAULT) -> None:
        super().__init__()
        if llc_type != LlcType.DEFAULT:
            raise ValueError("This LLC type is not yet implemented")
        if len(payload) > 1500:
            raise ValueError(f"The payload may not contain more than 1500 bytes, received {len(payload)} bytes.")
        self.size = len(payload).to_bytes(2, byteorder='big')
        if len(payload) < 42:
            payload = payload.zfill(42)

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

    def to_bits(self):
        return BitArray(bin=bin(int.from_bytes(self.bytes(), byteorder="big")))
