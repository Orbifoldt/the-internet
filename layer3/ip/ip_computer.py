from ipaddress import IPv4Address, IPv6Address
from typing import Optional

from layer2.arp.arp import ARPFrame, ARPPacket, extract_arp_packet, ARPOperation
from layer2.ethernet.ethernet import EthernetFrameBase, EthernetFrame, EtherType
from layer2.infrastructure.ethernet_devices import EthernetEndpoint
from layer2.mac import Mac
from layer3.ip.decoding import ipv4_packet_decoder
from layer3.ip.ipv4 import IPv4Packet, IPv4Header


# TODO: router discovery?
class ComputerWithIpCapability(EthernetEndpoint):
    def __init__(self, ip4: IPv4Address, ip6: IPv6Address, mac: Mac = None, name: str = ""):
        super().__init__(mac, name + f"({ip4})")
        self.ip4 = ip4
        self.ip6 = ip6
        self.ip4_cache: dict[IPv4Address, Mac] = {}
        self.ip6_cache: dict[IPv6Address, Mac] = {}

    def receive(self, incoming_interface_num: int = 0, **kwargs):
        frame: Optional[EthernetFrameBase] = super().receive(incoming_interface_num, **kwargs)
        if frame is None:
            return
        if isinstance(frame, EthernetFrame):
            if frame.ether_type == EtherType.ARP:
                self.process_arp(frame)
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
            self.send_arp_for(packet.destination)

        if packet.destination not in self.ip4_cache:
            self.say("Destination not found after ARP, sending packet to router")
            # TODO: set router as the target (ip or mac?)
            raise NotImplementedError("Router functionality not implemented yet.")
        else:
            target_mac = self.ip4_cache[packet.destination]
            self.say(f"Destination ip {packet.destination} has physical address {target_mac}.")
            if len(packet) > EthernetFrame.MAX_PAYLOAD:
                self.say("Packet too large, it needs fragmentation")
                raise NotImplementedError("Fragmentation not yet available")
            else:
                self.say("Sending packet now...")
                self.send_data(packet.bytes, target_mac, EtherType.IPV4)

    def send_arp_for(self, other_ip: IPv4Address):
        """ Send out an ARP request for the other_ip address to discover and store their mac address """
        arp_frame = ARPFrame(ARPPacket(self.mac, self.ip4, other_ip))
        self.send_frame(arp_frame)

    def process_arp(self, frame: EthernetFrame):
        arp_packet = extract_arp_packet(frame)
        if arp_packet.target_ip == self.ip4:
            self.store_arp_information(arp_packet)
            if arp_packet.operation == ARPOperation.REQUEST:
                self.respond_to_arp_request(arp_packet)
        else:
            self.say(f"Received ARP packet targeted at {arp_packet.target_ip}, dropping packet.")

    def store_arp_information(self, arp_packet: ARPPacket):
        self.say(f"Received ARP packet from {arp_packet.sender_ip}, storing their MAC {arp_packet.sender_mac}")
        self.ip4_cache[arp_packet.sender_ip] = arp_packet.sender_mac

    def respond_to_arp_request(self, arp_packet: ARPPacket):
        self.say(f"Received ARP request targeted at me ({arp_packet.target_ip}), responding with: {self.mac}.")
        response = arp_packet.get_response(self.mac)
        self.send_frame(response)

    def process_ipv4(self, frame: EthernetFrame):
        try:
            packet = ipv4_packet_decoder(frame.payload)
            self.say(f"Received from {packet.source} the following packet payload:\n    > {packet.payload}")
            return packet.payload
        except ValueError as e:
            self.say(f"Error while decoding packet inside frame from {frame.source}, it will be dropped. Cause:", e)
