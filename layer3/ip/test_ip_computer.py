from ipaddress import IPv4Address
from unittest import TestCase

from layer2.infrastructure.ethernet_devices import EthernetSwitch
from layer2.mac import Mac
from layer3.ip.ip_computer import ComputerWithIpCapability


class TestComputerWithIpCapability(TestCase):
    ip_a = IPv4Address("54.203.125.101")
    ip_b = IPv4Address("13.77.161.179")
    ip_c = IPv4Address("192.168.178.1")
    mac_a = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    mac_b = Mac.fromstring("1e:a1:d6:9d:23:53")
    mac_c = Mac.fromstring("ff:ee:dd:11:22:33")

    def setup_ab_network(self):
        self.comp_a = ComputerWithIpCapability(self.ip_a, None, self.mac_a, name="A ")
        self.comp_b = ComputerWithIpCapability(self.ip_b, None, self.mac_b, name="B ")
        self.comp_a.connect_to(self.comp_b, other_interface_num=0)

    def test_send_arp_between_two_directly_connected_computers(self):
        self.setup_ab_network()

        self.comp_a.send_arp_for(self.ip_b)

        self.assertTrue(self.ip_b in self.comp_a.ip4_cache)
        self.assertEqual(self.mac_b, self.comp_a.ip4_cache[self.ip_b])
        self.assertTrue(self.ip_a in self.comp_b.ip4_cache)
        self.assertEqual(self.mac_a, self.comp_b.ip4_cache[self.ip_a])
        """
        CONSOLE OUTPUT:
        
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received possible ARP from a1:b2:c3:d4:e5:f6, opening payload...
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received ARP packet from 54.203.125.101, storing their MAC a1:b2:c3:d4:e5:f6
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received ARP request targeted at me (13.77.161.179), responding with: 1e:a1:d6:9d:23:53.
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 1e:a1:d6:9d:23:53 the following frame data:
            > b'\x00\x01\x08\x00\x06\x04\x00\x02\x1e\xa1\xd6\x9d#S\rM\xa1\xb3\xa1\xb2\xc3\xd4\xe5\xf66\xcb}e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received ARP packet from 13.77.161.179, storing their MAC 1e:a1:d6:9d:23:53
        """

    def test_send_ip_packet_between_two_directly_connected_computers(self):
        self.setup_ab_network()

        self.comp_a.send_over_ip(self.ip_b, b"Hello there Bob! How are you today? This is my message sent with IP.")
        self.comp_b.send_over_ip(self.ip_a, b"Hi Alice, thanks for your message! You have my regards.")

        self.assertTrue(self.ip_b in self.comp_a.ip4_cache)
        self.assertEqual(self.mac_b, self.comp_a.ip4_cache[self.ip_b])
        self.assertTrue(self.ip_a in self.comp_b.ip4_cache)
        self.assertEqual(self.mac_a, self.comp_b.ip4_cache[self.ip_a])

        """
        CONSOLE OUTPUT:
        
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Unknown physical address for ip 13.77.161.179, sending out ARP
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received possible ARP from a1:b2:c3:d4:e5:f6, opening payload...
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received ARP packet from 54.203.125.101, storing their MAC a1:b2:c3:d4:e5:f6
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received ARP request targeted at me (13.77.161.179), responding with: 1e:a1:d6:9d:23:53.
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 1e:a1:d6:9d:23:53 the following frame data:
            > b'\x00\x01\x08\x00\x06\x04\x00\x02\x1e\xa1\xd6\x9d#S\rM\xa1\xb3\xa1\xb2\xc3\xd4\xe5\xf66\xcb}e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received ARP packet from 13.77.161.179, storing their MAC 1e:a1:d6:9d:23:53
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Destination ip 13.77.161.179 has physical address 1e:a1:d6:9d:23:53.
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Sending packet now...
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received from a1:b2:c3:d4:e5:f6 the following frame data:
            > b'E\x00\x00X\x00\x00@\x00\x80\x06\x97o6\xcb}e\rM\xa1\xb3Hello there Bob! How are you today? This is my message sent with IP.'
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received from 54.203.125.101 the following packet payload:
            > b'Hello there Bob! How are you today? This is my message sent with IP.'
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Destination ip 54.203.125.101 has physical address a1:b2:c3:d4:e5:f6.
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Sending packet now...
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 1e:a1:d6:9d:23:53 the following frame data:
            > b'E\x00\x00K\x00\x00@\x00\x80\x06\x97|\rM\xa1\xb36\xcb}eHi Alice, thanks for your message! You have my regards.'
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 13.77.161.179 the following packet payload:
            > b'Hi Alice, thanks for your message! You have my regards.'
        """

    def test_send_ip_packet_between_two_computers_with_switch_inbetween(self):
        comp_a = ComputerWithIpCapability(self.ip_a, None, self.mac_a, name="A ")
        comp_b = ComputerWithIpCapability(self.ip_b, None, self.mac_b, name="B ")
        switch = EthernetSwitch(2)
        comp_a.connect_to(switch, 0)
        comp_b.connect_to(switch, 1)

        comp_a.send_over_ip(self.ip_b, b"Hello there Bob! How are you today? This is my message sent with IP.")
        comp_b.send_over_ip(self.ip_a, b"Hi Alice, thanks for your message! You have my regards.")

        self.assertTrue(self.ip_b in comp_a.ip4_cache)
        self.assertEqual(self.mac_b, comp_a.ip4_cache[self.ip_b])
        self.assertTrue(self.ip_a in comp_b.ip4_cache)
        self.assertEqual(self.mac_a, comp_b.ip4_cache[self.ip_a])

        self.assertEqual(0, switch.cache[self.mac_a].interface_num)
        self.assertEqual(1, switch.cache[self.mac_b].interface_num)
        self.assertEqual(2, len(switch.cache))

        """
        CONSOLE OUTPUT:
        
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Unknown physical address for ip 13.77.161.179, sending out ARP
        [SWITCH]: Unknown target ff:ff:ff:ff:ff:ff, broadcasting frame to all
        [SWITCH]: [eth_1]: Forwarding frame from a1:b2:c3:d4:e5:f6 to ff:ff:ff:ff:ff:ff
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>: eth0]: Received ARP packet from 54.203.125.101, storing their MAC a1:b2:c3:d4:e5:f6
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>: eth0]: Received ARP request targeted at me (13.77.161.179), responding with: 1e:a1:d6:9d:23:53.
        [SWITCH]: Forwarding data from 1e:a1:d6:9d:23:53. Target a1:b2:c3:d4:e5:f6 was cached on interface 0
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>: eth0]: Received ARP packet from 13.77.161.179, storing their MAC 1e:a1:d6:9d:23:53
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Destination ip 13.77.161.179 has physical address 1e:a1:d6:9d:23:53.
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Sending packet now...
        [SWITCH]: Forwarding data from a1:b2:c3:d4:e5:f6. Target 1e:a1:d6:9d:23:53 was cached on interface 1
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received from a1:b2:c3:d4:e5:f6 the following frame data:
            > b'E\x00\x00X\x00\x00@\x00\x80\x06\x97o6\xcb}e\rM\xa1\xb3Hello there Bob! How are you today? This is my message sent with IP.'
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received from 54.203.125.101 the following packet payload:
            > b'Hello there Bob! How are you today? This is my message sent with IP.'
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Destination ip 54.203.125.101 has physical address a1:b2:c3:d4:e5:f6.
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Sending packet now...
        [SWITCH]: Forwarding data from 1e:a1:d6:9d:23:53. Target a1:b2:c3:d4:e5:f6 was cached on interface 0
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 1e:a1:d6:9d:23:53 the following frame data:
            > b'E\x00\x00K\x00\x00@\x00\x80\x06\x97|\rM\xa1\xb36\xcb}eHi Alice, thanks for your message! You have my regards.'
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 13.77.161.179 the following packet payload:
            > b'Hi Alice, thanks for your message! You have my regards.'
        """

    def test_send_ip_packet_between_three_computers_with_switch_inbetween(self):
        comp_a = ComputerWithIpCapability(self.ip_a, None, self.mac_a, name="A ")
        comp_b = ComputerWithIpCapability(self.ip_b, None, self.mac_b, name="B ")
        comp_c = ComputerWithIpCapability(self.ip_c, None, self.mac_c, name="C ")
        switch = EthernetSwitch(4)
        comp_a.connect_to(switch, 0)
        comp_b.connect_to(switch, 3)
        comp_c.connect_to(switch, 2)

        comp_a.send_over_ip(self.ip_b, b"Hello there Bob! How are you today? This is my message sent with IP.")
        comp_b.send_over_ip(self.ip_a, b"Hi Alice, thanks for your message! You have my regards.")

        self.assertTrue(self.ip_b in comp_a.ip4_cache)
        self.assertEqual(self.mac_b, comp_a.ip4_cache[self.ip_b])
        self.assertTrue(self.ip_a in comp_b.ip4_cache)
        self.assertEqual(self.mac_a, comp_b.ip4_cache[self.ip_a])

        self.assertEqual(0, switch.cache[self.mac_a].interface_num)
        self.assertEqual(3, switch.cache[self.mac_b].interface_num)
        self.assertEqual(2, len(switch.cache))

        """
        CONSOLE OUTPUT:

        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Unknown physical address for ip 13.77.161.179, sending out ARP
        [SWITCH]: Unknown target ff:ff:ff:ff:ff:ff, broadcasting frame to all
        [SWITCH]: [eth_2]: Forwarding frame from a1:b2:c3:d4:e5:f6 to ff:ff:ff:ff:ff:ff
        [COMPUTER_C (192.168.178.1) <ff:ee:dd:11:22:33>: eth0]: Received ARP packet targeted at 13.77.161.179, dropping packet.
        [SWITCH]: [eth_3]: Forwarding frame from a1:b2:c3:d4:e5:f6 to ff:ff:ff:ff:ff:ff
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>: eth0]: Received ARP packet from 54.203.125.101, storing their MAC a1:b2:c3:d4:e5:f6
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>: eth0]: Received ARP request targeted at me (13.77.161.179), responding with: 1e:a1:d6:9d:23:53.
        [SWITCH]: Forwarding data from 1e:a1:d6:9d:23:53. Target a1:b2:c3:d4:e5:f6 was cached on interface 0
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>: eth0]: Received ARP packet from 13.77.161.179, storing their MAC 1e:a1:d6:9d:23:53
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Destination ip 13.77.161.179 has physical address 1e:a1:d6:9d:23:53.
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Sending packet now...
        [SWITCH]: Forwarding data from a1:b2:c3:d4:e5:f6. Target 1e:a1:d6:9d:23:53 was cached on interface 3
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received from a1:b2:c3:d4:e5:f6 the following frame data:
            > b'E\x00\x00X\x00\x00@\x00\x80\x06\x97o6\xcb}e\rM\xa1\xb3Hello there Bob! How are you today? This is my message sent with IP.'
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Received from 54.203.125.101 the following packet payload:
            > b'Hello there Bob! How are you today? This is my message sent with IP.'
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Destination ip 54.203.125.101 has physical address a1:b2:c3:d4:e5:f6.
        [COMPUTER_B (13.77.161.179) <1e:a1:d6:9d:23:53>]: Sending packet now...
        [SWITCH]: Forwarding data from 1e:a1:d6:9d:23:53. Target a1:b2:c3:d4:e5:f6 was cached on interface 0
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 1e:a1:d6:9d:23:53 the following frame data:
            > b'E\x00\x00K\x00\x00@\x00\x80\x06\x97|\rM\xa1\xb36\xcb}eHi Alice, thanks for your message! You have my regards.'
        [COMPUTER_A (54.203.125.101) <a1:b2:c3:d4:e5:f6>]: Received from 13.77.161.179 the following packet payload:
            > b'Hi Alice, thanks for your message! You have my regards.'
        """

