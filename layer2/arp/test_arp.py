from ipaddress import IPv4Address
from unittest import TestCase

from layer2.arp.arp import ARPPacket, extract_arp_packet, ARPFrame, ARPOperation
from layer2.ethernet.ethernet import EtherType, EthernetFrame
from layer2.mac import Mac


class TestARP(TestCase):
    source_ip = IPv4Address("54.203.125.101")
    destination_ip = IPv4Address("13.77.161.179")
    source_mac = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    destination_mac = Mac.fromstring("1e:a1:d6:9d:23:53")

    def test_decoding_arp_packet_from_bytes(self):
        request_packet = ARPPacket(self.source_mac, self.source_ip, self.destination_ip)
        frame = ARPFrame(request_packet)
        decoded_packet = extract_arp_packet(frame)
        self.assertEqual(request_packet, decoded_packet)

    def test_generating_response_packet_for_request_has_correct_type_and_addresses(self):
        request_packet = ARPPacket(self.source_mac, self.source_ip, self.destination_ip)
        response_frame: EthernetFrame = request_packet.get_response(self.destination_mac)

        self.assertEqual(self.destination_mac, response_frame.source)
        self.assertEqual(self.source_mac, response_frame.destination)
        self.assertEqual(EtherType.ARP, response_frame.ether_type)

    def test_decoding_response_packet_from_bytes_has_right_info(self):
        request_packet = ARPPacket(self.source_mac, self.source_ip, self.destination_ip)
        response_frame = request_packet.get_response(self.destination_mac)
        decoded_packet: ARPPacket = extract_arp_packet(response_frame)

        self.assertEqual(EtherType.IPV4.bytes, decoded_packet.ptype)
        self.assertEqual(self.destination_mac.address, decoded_packet.sender_hw_addr)
        self.assertEqual(self.source_mac.address, decoded_packet.target_hw_addr)
        self.assertEqual(int(self.destination_ip).to_bytes(4, byteorder="big"), decoded_packet.sender_protocol_addr)
        self.assertEqual(int(self.source_ip).to_bytes(4, byteorder="big"), decoded_packet.target_protocol_addr)
        self.assertEqual(ARPOperation.REPLY.bytes, decoded_packet.operation_bytes)



