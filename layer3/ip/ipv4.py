from __future__ import annotations

from enum import Enum
from ipaddress import IPv4Address
from typing import Final

from bitstring import BitArray

from layer3.ip.shared import DSCP, ECN, IPProtocol
from layer3.tools import checksum


class IPv4Packet(object):
    VERSION: Final = 4

    def __init__(self, header: IPv4Header, payload: bytes):
        self.header = header
        self.payload = payload

    @staticmethod
    def default_packet(source: IPv4Address, destination: IPv4Address, payload: bytes,
                       protocol: IPProtocol = IPProtocol.TCP):
        header = IPv4Header.default_header(source, destination, len(payload), protocol)
        return IPv4Packet(header, payload)

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
        return self.header.destination_ip

    @property
    def is_valid(self) -> bool:
        return self.header.verify_checksum()

    def decrease_ttl(self) -> int:
        """ Decrease Time To Live of this packet and recalculate the header checksum. Returns remaining TTL. """
        return self.header.decrease_ttl()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.header == other.header and self.payload == other.payload


class IPv4Header(object):
    VERSION: Final = 4
    header_byte_len: Final = 20

    def __init__(self, dscp: DSCP, ecn: ECN, identification: int, flags: IPv4Flag, fragment_offset: int,
                 time_to_live: int, protocol: IPProtocol, payload_length: int, source: IPv4Address,
                 destination: IPv4Address, *options: IPv4Options):
        self.version = BitArray(uint=self.VERSION, length=4)
        self.dscp = dscp.bits
        self.ecn = ecn.bits
        self.identification = BitArray(uint=identification, length=16)
        self.flags = flags.bits
        self.fragment_offset = BitArray(uint=fragment_offset, length=13)
        self.time_to_live = BitArray(uint=time_to_live, length=8)
        self.protocol = protocol.bits
        self.header_checksum = BitArray(auto=16)
        self.source = BitArray(uint=int(source), length=32)
        self.destination = BitArray(uint=int(destination), length=32)
        self.options = sum(option.bits for option in options) if len(options) != 0 else BitArray(auto=0)

        self.ihl = self.calculate_ihl()
        self.total_length = self.calculate_packet_byte_len(payload_length)
        self.header_checksum = self.calculate_checksum()

        self.source_ip = source
        self.destination_ip = destination

    @property
    def bits(self):
        return self.version + self.ihl + self.dscp + self.ecn + self.total_length + self.identification + self.flags + \
               self.fragment_offset + self.time_to_live + self.protocol + self.header_checksum + self.source + \
               self.destination + self.options

    @property
    def bytes(self):
        return self.bits.bytes

    def calculate_ihl(self) -> BitArray:
        """ Number of 32 bit words in the header, i.e. the number of bytes in this header divided by 4 """
        num_bits = 5 * 32 + len(self.options)
        if num_bits % 32 != 0:
            raise ValueError(f"Expected multiple of 32 bits, but found {num_bits}")
        return BitArray(uint=int(num_bits / 32), length=4)

    def calculate_packet_byte_len(self, data_length: int) -> BitArray:
        return BitArray(uint=data_length + 4 * self.ihl.uint, length=16)

    def calculate_checksum(self) -> BitArray:
        """
        Calculate the checksum of this header. This does not mutate the existing value of self.header_checksum, rather
        it assumes it to be all 0's. Checksum is calculated as specified in rfc791:
            'The checksum field is the 16-bit ones' complement of the ones' complement sum of all 16-bit words in the
            header. For purposes of computing the checksum, the value of the checksum field is zero.'
        It's returned as the bits representing the value in bytes with the most significant byte at the end.
        """
        old_checksum = self.header_checksum
        self.header_checksum = BitArray(auto=16)  # set checksum bits to all 0 before calculating checksum
        new_checksum = checksum(self.bits)
        self.header_checksum = old_checksum
        return new_checksum

    def verify_checksum(self) -> bool:
        """ Returns true if the checksum is valid. This is calculated by simply recalculating the checksum of the bits
        ithout setting the checksum bits to 0. If this returns all 0's then the checksum is valid"""
        return checksum(self.bits) == BitArray(auto=16)

    def overwrite_checksum(self, header_checksum: BitArray):
        if not len(header_checksum) == 16:
            raise ValueError
        self.header_checksum = header_checksum
        return self

    def decrease_ttl(self) -> int:
        """ Decrease the Time To Live by one and recalculate the checksum """
        new_ttl = int(self.time_to_live.bin, 2) - 1
        self.time_to_live = BitArray(uint=new_ttl, length=8)
        self.header_checksum = BitArray(auto=16)
        self.header_checksum = self.calculate_checksum()
        return new_ttl

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.bits == other.bits

    @staticmethod
    def default_header(source: IPv4Address, destination: IPv4Address, data_len: int, protocol=IPProtocol.TCP, ttl=128):
        return IPv4Header(dscp=DSCP.CS0, ecn=ECN.NON_ECT, identification=0, flags=IPv4Flag(True, False),
                          fragment_offset=0, time_to_live=ttl, protocol=protocol, payload_length=data_len,
                          source=source, destination=destination)


class IPv4Flag(object):
    """ This controls fragmentation of a packet """

    def __init__(self, df: bool, mf: bool):
        self.df = df  # Don't Fragment -> if True and fragmentation is required for routing then packet is dropped
        self.mf = mf  # More Fragments -> False for non-fragmented, True for all except last fragmented packet

    @property
    def bits(self):
        return BitArray(auto=[0, 1 if self.df else 0, 1 if self.mf else 0])

    @classmethod
    def from_bits(cls, bits: BitArray):
        if bits[0]:
            raise ValueError("First bit of IPv4 flag must be 0")
        return IPv4Flag(bits[1] == 1, bits[2] == 1)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.df == other.df and self.mf == other.mf


class IPv4Options(Enum):
    """
    Optional options that may be added at the end of the IPv4 header.
    """
    EOOL = 0x00, "End of Option List"
    NOP = 0x01, "No Operation"
    SEC = 0x02, "Security (defunct)"
    RR = 0x07, "Record Route"
    ZSU = 0x0A, "Experimental Measurement"
    MTUP = 0x0B, "MTU Probe"
    MTUR = 0x0C, "MTU Reply"
    ENCODE = 0x0F, "ENCODE"
    QS = 0x19, "Quick-Start"
    EXP = 0x1E, "RFC3692-style Experiment"
    TS = 0x44, "Time Stamp"
    TR = 0x52, "Traceroute"
    EXP2 = 0x5E, "RFC3692-style Experiment"
    SEC2 = 0x82, "Security (RIPSO)"
    LSR = 0x83, "Loose Source Route"
    E_SEC = 0x85, "Extended Security (RIPSO)"
    CIPSO = 0x86, "Commercial IP Security Option"
    SID = 0x88, "Stream ID"
    SSR = 0x89, "Strict Source Route"
    VISA = 0x8E, "Experimental Access Control"
    IMITD = 0x90, "IMI Traffic Descriptor"
    EIP = 0x91, "Extended Internet Protocol"
    ADDEXT = 0x93, "Address Extension"
    RTRALT = 0x94, "Router Alert"
    SDB = 0x95, "Selective Directed Broadcast"
    DPS = 0x97, "Dynamic Packet State"
    UMP = 0x98, "Upstream Multicast Pkt."
    EXP3 = 0x9E, "RFC3692-style Experiment"
    FINN = 0xCD, "Experimental Flow Control"
    EXP4 = 0xDE, "RFC3692-style Experiment"

    def __init__(self, int_value, description):
        self.int_value = int_value
        self.description = description

    @property
    def bits(self):
        return BitArray(uint=self.int_value, length=32)

    @classmethod
    def from_int(cls, n: int) -> IPv4Options:
        matching_entries = [option for option in cls if option.int_value == n]
        if len(matching_entries) == 0:
            raise ValueError(f"Invalid value '{n}', no IPv4 option found with this value.")
        return matching_entries[0]
