from ipaddress import IPv4Address, IPv4Network, ip_network, ip_address
from unittest import TestCase

from layer2.infrastructure.ethernet_devices import EthernetEndpointWithArp
from layer2.infrastructure.network_interface import EthernetInterfaceWithArp, HdlcInterface
from layer2.mac import Mac
from layer3.ip.ip_computer import ComputerWithIpCapability
from layer3.ip.ip_router import IpRouter


class TestIpRouter(TestCase):
    macA = Mac.fromstring("AA:AA:AA:AA:AA:AA")
    macB = Mac.fromstring("BB:BB:BB:BB:BB:BB")
    ip_a = IPv4Address("192.168.178.2")
    ip_b = IPv4Address("10.99.0.2")
    computer_A = ComputerWithIpCapability(ip_a, None, macA, "A")
    computer_B = ComputerWithIpCapability(ip_b, None, macB, "B")

    def test_sending_ip_packet_between_two_networks_connected_by_a_router(self):
        mac_router = Mac.fromstring("CE:CE:CE:CE:CE:CE")
        ip_router_internal = IPv4Address("192.168.178.1")
        ip_router_external = IPv4Address("10.0.0.1")
        router_eth0 = EthernetInterfaceWithArp(0, None, ip_router_internal, mac_router)
        router_eth1 = EthernetInterfaceWithArp(1, None, ip_router_external, mac_router)
        router = IpRouter([router_eth0, router_eth1], "Router")
        router.interface_networks[1] = ip_network("10.0.0.0/8")  # manually broadening the netmask

        self.computer_A.connect_to(router, 0)
        self.computer_B.connect_to(router, 1)

        self.computer_A.send_over_ip(target_ip4=self.ip_b, data=b"Hello there Bob, how is it outside the network? Bye!")

        print("\n Now responding without default gateway settings...")
        self.computer_B.send_over_ip(self.ip_a, b"Hello back at you Bob, kisses from Alice...")

        print("\n Let's fix this, we set B's default gateway to 10.0.0.1, the routers ip on this network")
        self.computer_B.default_gateway_ip4 = ip_address('10.0.0.1')
        self.computer_B.send_over_ip(self.ip_a, b"Hello back at you Bob, kisses from Alice...")
        """
        CONSOLE OUTPUT
        
        [COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>]: Unknown physical address for ip 10.99.0.2, sending out ARP
        [ROUTER_Router]: <[eth0]>: Received ARP packet targeted at 10.99.0.2, dropping packet.
        [COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>]: Destination not found after ARP, sending packet to default gateway
        [COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>]: Unknown physical address for ip 192.168.178.1, sending out ARP
        [ROUTER_Router]: <[eth0]>: Received ARP packet from 192.168.178.2, storing their MAC aa:aa:aa:aa:aa:aa
        [ROUTER_Router]: <[eth0]>: Received ARP request targeted at me (192.168.178.1), responding with: ce:ce:ce:ce:ce:ce.
        [COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>]: <[COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>: eth0]>: Received ARP packet from 192.168.178.1, storing their MAC ce:ce:ce:ce:ce:ce
        [ROUTER_Router]: Received ethernet frame...
        [ROUTER_Router]: Received from 192.168.178.2 the following packet payload:
            > b'Hello there Bob, how is it outside the network? Bye!'
        [ROUTER_Router]: Processing ipv4 packet...
        [ROUTER_Router]: Destination is local on interface 1
        [ROUTER_Router]: Unknown physical address for target 10.99.0.2, sending out ARP...
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: <[COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>: eth0]>: Received ARP packet from 10.0.0.1, storing their MAC ce:ce:ce:ce:ce:ce
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: <[COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>: eth0]>: Received ARP request targeted at me (10.99.0.2), responding with: bb:bb:bb:bb:bb:bb.
        [ROUTER_Router]: <[eth1]>: Received ARP packet from 10.99.0.2, storing their MAC bb:bb:bb:bb:bb:bb
        [ROUTER_Router]: Physical address for target 10.99.0.2 is known to be bb:bb:bb:bb:bb:bb
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Received from ce:ce:ce:ce:ce:ce the following frame data:
            > b'E\x00\x00H\x00\x00@\x00\x7f\x06~\xa0\xc0\xa8\xb2\x02\nc\x00\x02Hello there Bob, how is it outside the network? Bye!'
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Received from 192.168.178.2 the following packet payload:
            > b'Hello there Bob, how is it outside the network? Bye!'
        
         Now responding without default gateway settings...
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Unknown physical address for ip 192.168.178.2, sending out ARP
        [ROUTER_Router]: <[eth1]>: Received ARP packet targeted at 192.168.178.2, dropping packet.
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Destination not found after ARP, sending packet to default gateway
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Unknown physical address for ip 192.168.178.1, sending out ARP
        [ROUTER_Router]: <[eth1]>: Received ARP packet targeted at 192.168.178.1, dropping packet.
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Unknown physical address for ip 192.168.178.1, dropping packet.
        
         Let's fix this, we set B's default gateway to 10.0.0.1, the routers ip on this network
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Unknown physical address for ip 192.168.178.2, sending out ARP
        [ROUTER_Router]: <[eth1]>: Received ARP packet targeted at 192.168.178.2, dropping packet.
        [COMPUTER_B(10.99.0.2) <bb:bb:bb:bb:bb:bb>]: Destination not found after ARP, sending packet to default gateway
        [ROUTER_Router]: Received ethernet frame...
        [ROUTER_Router]: Received from 10.99.0.2 the following packet payload:
            > b'Hello back at you Bob, kisses from Alice...'
        [ROUTER_Router]: Processing ipv4 packet...
        [ROUTER_Router]: Destination is local on interface 0
        [ROUTER_Router]: Physical address for target 192.168.178.2 is known to be aa:aa:aa:aa:aa:aa
        [COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>]: Received from ce:ce:ce:ce:ce:ce the following frame data:
            > b'E\x00\x00?\x00\x00@\x00\x7f\x06~\xa9\nc\x00\x02\xc0\xa8\xb2\x02Hello back at you Bob, kisses from Alice...'
        [COMPUTER_A(192.168.178.2) <aa:aa:aa:aa:aa:aa>]: Received from 10.99.0.2 the following packet payload:
            > b'Hello back at you Bob, kisses from Alice...'
        
        """

    def test_sending_ip_packet_over_default_gateway(self):
        mac_router_a = Mac.fromstring("CE:CE:CE:CE:CE:CE")
        router_a_internal_ip = IPv4Address("192.168.178.1")
        router_a_external_ip = IPv4Address("10.0.0.1")  # TODO: hmm this is not necessary for HDLC? Or is it?
        router_a_eth0 = EthernetInterfaceWithArp(0, None, router_a_internal_ip, mac_router_a)
        router_a_hdlc1 = HdlcInterface(1, None)
        router_a = IpRouter([router_a_eth0, router_a_hdlc1], "Router A")
        router_a.default_interface_num = 1
        
        mac_router_b = Mac.fromstring("DD:DD:DD:DD:DD:DD")
        router_b_internal_ip = IPv4Address("192.168.178.1")
        router_b_external_ip = IPv4Address("10.0.0.2")
        router_b_eth0 = EthernetInterfaceWithArp(0, None, router_b_internal_ip, mac_router_b)
        router_b_hdlc1 = HdlcInterface(1, None)
        router_b = IpRouter([router_b_eth0, router_b_hdlc1], "Router B")
        router_b.default_interface_num = 1

        self.computer_A.connect_to(router_a, 0)
        self.computer_B.connect_to(router_b, 0)
        router_a.connect_to(router_b, 1, 1)

        self.computer_A.send_over_ip(target_ip4=self.ip_b, data=b"Hello there Bob, how is it outside the network? Bye!")
        # TODO: implement sending over HDLC and PPP for ip routers

        


