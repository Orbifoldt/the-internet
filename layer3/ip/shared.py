from __future__ import annotations

from enum import Enum
from bitstring import BitArray


class DSCP(Enum):
    """
    Differentiated services code point: used in IP networks to classify and consequently manage network traffic based
    on the carried information, i.e. to prioritize traffic to provide quality of service (QoS).
    As specified in rfc4594 (https://datatracker.ietf.org/doc/html/rfc4594) these are the recommended values.
    """
    CS6 = 0b110000, "Network Control", "Network routing"
    EF = 0b101110, "Telephony", "IP Telephony bearer"
    CS5 = 0b101000, "Signaling", "IP Telephony signaling"
    AF41 = 0b100010, "Multimedia Conferencing", "H.323/V2 video  conferencing (adaptive)"
    AF42 = 0b100100, "Multimedia Conferencing", "H.323/V2 video  conferencing (adaptive)"
    AF43 = 0b100110, "Multimedia Conferencing", "H.323/V2 video  conferencing (adaptive)"
    CS4 = 0b100000, "Real-Time Interactive", "Video conferencing and Interactive gaming"
    AF31 = 0b011010, "Multimedia Streaming", "Streaming video and audio on demand"
    AF32 = 0b011100, "Multimedia Streaming", "Streaming video and audio on demand"
    AF33 = 0b011110, "Multimedia Streaming", "Streaming video and audio on demand"
    CS3 = 0b011000, "Broadcast Video", "Broadcast TV & live events"
    AF21 = 0b010010, "Low-Latency Data", "Client/server transactions  Web-based ordering"
    AF22 = 0b010100, "Low-Latency Data", "Client/server transactions  Web-based ordering"
    AF23 = 0b010110, "Low-Latency Data", "Client/server transactions  Web-based ordering"
    CS2 = 0b010000, "OAM", " OAM&Pg"
    AF11 = 0b001010, "High-Throughput Data", "Store and forward applications"
    AF12 = 0b001100, "High-Throughput Data", "Store and forward applications"
    AF13 = 0b001110, "High-Throughput Data", "Store and forward applications"
    DF = 0b000000, "Standard", "Undifferentiated applications"
    CS0 = DF
    CS1 = 0b001000, "Low-Priority Data", "Any flow that has no BW  assurance"

    def __init__(self, dscp_value, service_class_name, examples):
        self.dscp_value = dscp_value
        self.service_class_name = service_class_name
        self.examples = examples

    @property
    def bits(self):
        return BitArray(uint=self.dscp_value, length=6)

    @classmethod
    def from_int(cls, n: int) -> DSCP:
        matching_entries = [dscp for dscp in cls if dscp.dscp_value == n]
        if len(matching_entries) == 0:
            raise ValueError
        return matching_entries[0]


class ECN(Enum):
    """
    Explicit Congestion Notification: extension to IP/TCP to allow end2end notification of congestion without
    having to drop packets.
    """
    NON_ECT = 0b00  # Non ECN capable transport
    ECT_0 = 0b10  # ECN capable transport
    ECT_1 = 0b01  # ECN capable transport
    CE = 0b11  # Congestion Encountered

    @property
    def bits(self):
        return BitArray(uint=self.value, length=2)


class IPProtocol(Enum):
    """
    A selection of IP protocol numbers which describes the encapsulated protocol, i.e. what the layout is of the payload
    This is an 8 bit field in both the IPv4 and IPv6 headers.
    """
    ICMP = 1, "Internet Control Message Protocol"
    IGMP = 2, "Internet Group Management Protocol"
    TCP = 6, "Transmission Control Protocol"
    UDP = 17, "User Datagram Protocol"
    ENCAP = 41, "IPv6 encapsulation"
    OSPF = 89, "Open Shortest Path First"
    SCTP = 132, "Stream Control Transmission Protocol"

    def __init__(self, int_value, description):
        self.int_value = int_value
        self.description = description

    @property
    def bits(self):
        return BitArray(uint=self.int_value, length=8)

    @classmethod
    def from_int(cls, n: int) -> IPProtocol:
        matching_entries = [ipp for ipp in cls if ipp.int_value == n]
        if len(matching_entries) == 0:
            raise ValueError
        return matching_entries[0]
