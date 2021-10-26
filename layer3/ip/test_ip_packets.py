from ipaddress import IPv4Address, IPv6Address
from unittest import TestCase

from bitstring import BitArray

from layer3.ip.decoding import packet_decoder, get_ip_version
from layer3.ip.ipv4 import IPv4Header, IPv4Flag, IPv4Options, IPv4Packet
from layer3.ip.ipv6 import IPv6Header, IPv6Packet
from layer3.ip.shared import DSCP, IPProtocol, ECN


class Test(TestCase):
    payload = b"This is my ASCII encoded payload! Take good care of it. This has an uneven number of bytes@"

    source4 = IPv4Address("54.203.125.101")
    destination4 = IPv4Address("13.77.161.179")
    ip4header = IPv4Header(DSCP.CS3, ECN.ECT_1, 745, IPv4Flag(True, False), 0, 72, IPProtocol.UDP, len(payload),
                           source4, destination4, IPv4Options.DPS, IPv4Options.EXP4, IPv4Options.VISA)
    ip4packet = IPv4Packet(ip4header, payload)

    source6 = IPv6Address("2a02:26f0:d7::216:3649")
    destination6 = IPv6Address("2a05:d018:76c:b685:c898:aa3a:42c7:9d21")
    ip6header = IPv6Header(DSCP.AF33, ECN.NON_ECT, 95, len(payload), IPProtocol.ICMP, 55, source6, destination6)
    ip6packet = IPv6Packet(ip6header, payload)

    def test_ipv4_from_bytes(self):
        ip4bytes = self.ip4packet.bytes
        decoded_packet = packet_decoder(ip4bytes)
        self.assertEqual(4, get_ip_version(ip4bytes))
        self.assertEqual(self.ip4packet, decoded_packet)

    def test_ipv6_from_bytes(self):
        ip6bytes = self.ip6packet.bytes
        decoded_packet = packet_decoder(ip6bytes)
        self.assertEqual(6, get_ip_version(ip6bytes))
        self.assertEqual(self.ip6packet, decoded_packet)

    def test_ipv4_packet_is_valid(self):
        self.assertEqual(self.source4, self.ip4packet.source)
        self.assertEqual(self.destination4, self.ip4packet.destination)
        self.assertEqual(self.payload, self.ip4packet.payload)
        self.assertTrue(self.ip4packet.is_valid)

    def test_decrease_ttl_ipv4(self):
        packet = IPv4Packet.default_packet(self.source4, self.destination4, self.payload)
        old_ttl = packet.header.time_to_live.uint
        old_checksum = packet.header.header_checksum
        self.assertTrue(packet.is_valid)

        packet.decrease_ttl()

        self.assertEqual(old_ttl - 1, packet.header.time_to_live.uint)
        self.assertNotEqual(old_checksum, packet.header.header_checksum)
        self.assertTrue(packet.is_valid)

    def test_default_ipv4_from_bytes(self):
        packet = IPv4Packet.default_packet(self.source4, self.destination4, self.payload)
        ip4bytes = packet.bytes
        decoded_packet = packet_decoder(ip4bytes)
        self.assertEqual(packet, decoded_packet)

    def test_default_ipv4_from_bytes_with_invalid_checksum(self):
        packet = IPv4Packet.default_packet(self.source4, self.destination4, self.payload)
        packet.header.identification = BitArray(uint=1, length=16)  # Mutate the packet without changing the checksum
        ip4bytes = packet.bytes
        with self.assertRaises(ValueError):
            packet_decoder(ip4bytes)

    def test_decrease_ttl_ipv6(self):
        packet = IPv6Packet.default_packet(self.source6, self.destination6, self.payload)
        old_hop = packet.header.hop_limit.uint
        packet.decrease_hop_limit()
        self.assertEqual(old_hop - 1, packet.header.hop_limit.uint)

    def test_default_ipv6_from_bytes(self):
        packet = IPv6Packet.default_packet(self.source6, self.destination6, self.payload)
        ip6bytes = packet.bytes
        decoded_packet = packet_decoder(ip6bytes)
        self.assertEqual(packet, decoded_packet)

    def test_DSCP(self):
        dscp = DSCP.from_int(0b100110)
        self.assertEqual(DSCP.AF43, dscp)

    def test_ECN(self):
        ecn = ECN(0b10)
        self.assertEqual(ECN.ECT_0, ecn)

    def test_IPProtocol(self):
        protocol = IPProtocol.from_int(132)
        self.assertEqual(IPProtocol.SCTP, protocol)

    def test_IPv4Options(self):
        option = IPv4Options.from_int(0x93)
        self.assertEqual(IPv4Options.ADDEXT, option)

    def test_IPv4Flag(self):
        flag = IPv4Flag.from_bits(BitArray(bin="001"))
        self.assertEqual(IPv4Flag(False, True), flag)
