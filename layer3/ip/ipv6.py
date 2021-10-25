from __future__ import annotations

from ipaddress import IPv6Address
from typing import Final
from bitstring import BitArray

from layer3.ip.shared import DSCP, ECN, IPProtocol


class IPv6Packet(object):
    VERSION: Final = 6

    def __init__(self, source: IPv6Address, destination: IPv6Address, payload: bytes):
        self.header = IPv6Header.default_header(source, destination, len(payload))   # TODO
        self.payload = payload

    @property
    def bytes(self):
        return self.header.bytes + self.payload

    @property
    def bits(self):
        return BitArray(auto=self.bytes)

    @property
    def source(self):
        return self.header.source_ip

    @property
    def destination(self):
        return self.header.destination

    def decrease_hop_limit(self):
        self.header.decrease_hop_limit()


class IPv6Header(object):
    VERSION: Final = 6
    header_byte_leng = 40

    def __init__(self, dscp: DSCP, ecn: ECN, flow_label: int, payload_len: int, next_header: IPProtocol, hop_limit: int,
                 source: IPv6Address, destination: IPv6Address, *options):
        self.version = BitArray(uint=self.VERSION, length=4)
        self.dscp = dscp.bits
        self.ecn = ecn.bits
        self.flow_label = BitArray(uint=flow_label, length=20)
        self.payload_len = BitArray(uint=payload_len, length=16)  # + len of options
        self.next_header = next_header.bits
        self.hop_limit = BitArray(uint=hop_limit, length=8)
        self.source = BitArray(uint=int(source), length=128)
        self.destination = BitArray(uint=int(destination), length=128)

        self.source_ip = source
        self.destination_ip = destination

    @property
    def traffic_class(self):
        return self.dscp + self.ecn

    @property
    def bits(self):
        return self.version + self.traffic_class + self.flow_label + self.payload_len + self.next_header + \
               self.hop_limit + self.source + self.destination

    @property
    def bytes(self):
        return self.bits.bytes

    def decrease_hop_limit(self):
        new_hop_limit = int(self.hop_limit.bin, 2) - 1
        self.hop_limit = BitArray(uint=new_hop_limit, length=8)
        return new_hop_limit

    @staticmethod
    def default_header(source: IPv6Address, destination: IPv6Address, data_len: int) -> IPv6Header:
        raise NotImplementedError
