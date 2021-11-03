from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional, Callable

from layer2.arp.arp import ARPFrame, ARPPacket, extract_arp_packet, ARPOperation
from layer2.ethernet.ethernet import EthernetFrameBase, EthernetFrame, EtherType
from layer2.infrastructure.ethernet_devices import EthernetEndpointWithArp
from layer2.infrastructure.network_error import NetworkError
from layer2.mac import Mac
from layer3.ip.decoding import ipv4_packet_decoder
from layer3.ip.ipv4 import IPv4Packet, IPv4Header


class ComputerWithIpCapability(EthernetEndpointWithArp):
    def __init__(self, ip4: IPv4Address, ip6: IPv6Address, mac: Mac = None, name: str = ""):
        super().__init__(ip4, mac, name + f"({ip4})")
        self.ip4 = ip4
        self.ip6 = ip6
        self.ip6_cache: dict[IPv6Address, Mac] = {}
        self.default_gateway_ip4 = ip_address('192.168.178.1')

    @property
    def ip4_cache(self):
        return self.get_interface(0).ip4_cache

    def receive(self, frame: EthernetFrameBase, incoming_interface_num: int = 0):
        frame: Optional[EthernetFrameBase] = super().receive(frame, incoming_interface_num)
        if frame is None:
            return
        if isinstance(frame, EthernetFrame):
            if frame.ether_type == EtherType.ARP:
                raise NetworkError("Arp should not reach this point...")
            elif frame.ether_type == EtherType.IPV4:
                ip_payload = self.process_ipv4(frame)
                return ip_payload
            else:
                raise NotImplementedError(f"Ether type {frame.ether_type} not yet supported")  # TODO: implement ipv6
        else:
            self.say("Unsupported frame received, dropping it.")

    def send_over_ip(self, target_ip4: IPv4Address, data: bytes):
        packet = IPv4Packet(header=IPv4Header.default_header(self.ip4, target_ip4, len(data)), payload=data)
        self.send_ip_packet(packet)

    def send_ip_packet(self, packet: IPv4Packet):
        if packet.destination not in self.ip4_cache:
            self.say(f"Unknown physical address for ip {packet.destination}, sending out ARP")
            self.get_interface(0).send_arp_for(packet.destination)

        if packet.destination not in self.ip4_cache:
            self.say("Destination not found after ARP, sending packet to default gateway")
            self.send_packet_to_gateway(packet)
        else:
            target_mac = self.ip4_cache[packet.destination]
            self.say(f"Destination ip {packet.destination} has physical address {target_mac}.")
            if len(packet) > EthernetFrame.MAX_PAYLOAD:
                self.say("Packet too large, it needs fragmentation")
                raise NotImplementedError("Fragmentation not yet available")
            else:
                self.say("Sending packet now...")
                self.send_data(packet.bytes, target_mac, EtherType.IPV4)

    def send_packet_to_gateway(self, packet: IPv4Packet):
        if self.default_gateway_ip4 not in self.ip4_cache:
            self.say(f"Unknown physical address for ip {self.default_gateway_ip4}, sending out ARP")
            self.get_interface(0).send_arp_for(self.default_gateway_ip4)

        if self.default_gateway_ip4 not in self.ip4_cache:
            self.say(f"Unknown physical address for ip {self.default_gateway_ip4}, dropping packet.")
            return
        else:
            self.send_data(packet.bytes, self.ip4_cache[self.default_gateway_ip4])

    def process_ipv4(self, frame: EthernetFrame):
        try:
            packet = ipv4_packet_decoder(frame.payload)
            self.say(f"Received from {packet.source} the following packet payload:\n    > {packet.payload}")
            return packet.payload
        except ValueError as e:
            self.say(f"Error while decoding packet inside frame from {frame.source}, it will be dropped. Cause:", e)






