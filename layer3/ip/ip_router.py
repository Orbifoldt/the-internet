from __future__ import annotations

from enum import Enum
from ipaddress import IPv4Address, IPv4Network
from typing import List, Optional

from layer2.arp.arp import ARPPacket, ARPFrame, extract_arp_packet, ARPOperation
from layer2.ethernet.decoding import decode_frame
from layer2.ethernet.ethernet import EthernetFrame, EtherType, EthernetFrameBase
from layer2.hdlc.hdlc import HdlcFrame
from layer2.infrastructure.network_error import NetworkError
from layer2.infrastructure.network_interface import DeviceWithInterfaces, NetworkInterface, EthernetInterface, \
    HdlcInterface, PppInterface, EthernetInterfaceWithArp
from layer2.mac import Mac
from layer2.ppp.point_to_point import PppFrame
from layer3.ip.decoding import packet_decoder, ipv4_packet_decoder
from layer3.ip.ip_computer import ComputerWithIpCapability
from layer3.ip.ipv4 import IPv4Packet, IPv4Header
from layer3.ip.ipv6 import IPv6Packet
from layer3.ip.shared import IPProtocol
from layer3.trie.routing_table import IPv4RoutingTable, IPv6RoutingTable


class IpRouter(DeviceWithInterfaces):  # A pure router. Consumer routers do have a switch built in

    def __init__(self, interfaces: List[NetworkInterface], name: str):
        super().__init__(len(interfaces), name, name_prefix="ROUTER")
        self._interfaces = [interface for interface in interfaces]
        self.forwarding_table_v6: IPv6RoutingTable[int] = IPv6RoutingTable()

        self.forwarding_table_v4: IPv4RoutingTable[int] = IPv4RoutingTable()
        self.interface_networks: dict[int, IPv4Network] = {}
        self.interface_addresses: dict[int, IPv4Address] = {}

        for i, interface in enumerate(interfaces):
            interface.parent = self
            if isinstance(interface, EthernetInterfaceWithArp):
                self.interface_addresses[i] = interface.ip4
                self.interface_networks[i] = IPv4Network((interface.ip4, 24), strict=False)
            else:
                print("WARNING! Interface without IP address!!")

    def send(self, packet, outgoing_interface_num: int) -> None:
        interface = self.get_interface(outgoing_interface_num)
        # Encapsulate the packet into a frame appropriate for the given interface
        if isinstance(interface, EthernetInterfaceWithArp):
            target_mac = self.get_target_mac(outgoing_interface_num, packet.destination)
            frame = EthernetFrame(target_mac, interface.mac, packet.bytes, EtherType.IPV4)
        elif isinstance(interface, HdlcInterface):
            raise NotImplementedError  # TODO
            # frame = HdlcFrame(0, None, packet.bytes)
        elif isinstance(interface, PppInterface):
            raise NotImplementedError  # TODO
            # frame = PppFrame(PppProtocol.IPv4, packet.bytes)
        else:
            raise NetworkError(f"Interface {outgoing_interface_num} has unsupported type, can't sent out data.")

        # Then send that frame over the interface
        super().send(frame, outgoing_interface_num)

    def get_target_mac(self, interface_num: int, ip_dest: IPv4Address):
        interface = self.get_interface(interface_num)
        if not isinstance(interface, EthernetInterfaceWithArp):
            raise NetworkError(f"Interface {interface_num} is not an Ethernet Interface with ARP, cannot find mac")
        cache = interface.ip4_cache
        if ip_dest not in cache.keys():
            self.say(f"Unknown physical address for target {ip_dest}, sending out ARP...")
            interface.send_arp_for(ip_dest)
        if ip_dest not in cache.keys():
            raise NetworkError(f"Unknown target {ip_dest}, no response from ARP on interface {interface_num}.")
        else:
            self.say(f"Physical address for target {ip_dest} is known to be {cache[ip_dest]}")
            return cache[ip_dest]

    def receive(self, frame, incoming_interface_num: int) -> None:
        # Process the frame, and if appropriate extract the contained packet
        if isinstance(self.get_interface(incoming_interface_num), EthernetInterfaceWithArp):
            packet = self.process_ethernet_frame(frame, incoming_interface_num)
        elif isinstance(self.get_interface(incoming_interface_num), HdlcInterface):
            packet = self.process_hdlc_frame(frame)
        elif isinstance(self.get_interface(incoming_interface_num), PppInterface):
            packet = self.process_ppp_frame(frame)
        else:
            raise NetworkError(f"Interface {incoming_interface_num} has unsupported type, can't process incoming data.")

        # If a packet was contained in the frame we process it
        if packet is not None:
            if isinstance(packet, IPv4Packet):
                try:
                    self.process_ipv4_packet(packet, incoming_interface_num)
                except NetworkError:
                    self.nack(packet, frame, incoming_interface_num)

    def process_ipv4_packet(self, packet: IPv4Packet, incoming_interface_num: int):
        self.say("Processing ipv4 packet...")
        destination = packet.destination

        # Check if packet is addressed at self
        if destination == self.interface_addresses[incoming_interface_num]:
            self.say(f"Received packet addressed at me! Payload:\n    > {packet.payload}")
            return

        # Check if packet is addressed at something local to this router
        for (interface_num, subnet) in self.interface_networks.items():
            if destination in subnet:
                self.send_ipv4_local(packet, interface_num)
                return

        # Check if a route is known for the destination
        try:
            netw = self.forwarding_table_v4.find_best_match(destination)
            out_interface_num = self.forwarding_table_v4[netw]
            self.forward_ipv4(packet, out_interface_num)
            return
        # Forward packet over default route
        except KeyError:
            if self.default_interface_num is not None:
                self.forward_ipv4_default(packet)
            else:
                # If no default then an NetworkError will be raised and ICMP error-response is returned to sender
                self.nack(packet, None, incoming_interface_num)

    def send_ipv4_local(self, packet, interface_num: int):
        self.say(f"Destination is local on interface {interface_num}")
        packet.decrease_ttl()
        self.send(packet, interface_num)

    def forward_ipv4(self, packet, interface_num: int):
        self.say(f"Found route for destination, forwarding on interface {interface_num}")
        packet.decrease_ttl()
        self.send(packet, interface_num)

    def forward_ipv4_default(self, packet):
        self.say(f"No route found for destination, forwarding to default")
        packet.decrease_ttl()
        self.send(packet, self.default_interface_num)

    def nack(self, packet, frame, incoming_interface_num: int):
        error_msg: bytes = bytes()  # TODO
        header = IPv4Header.default_header(packet.source, packet.source, len(error_msg), IPProtocol.ICMP)
        # self.send(IPv4Packet(header, error_msg), incoming_interface_num)
        raise NotImplementedError

    def process_ethernet_frame(self, frame: EthernetFrameBase, incoming_interface_num: int) -> Optional[bytes]:
        if not isinstance(frame, EthernetFrameBase):
            raise NetworkError("Expected to receive an ethernet frame on an ethernet interface")
        self.say("Received ethernet frame...")

        if isinstance(frame, EthernetFrame):
            if frame.ether_type == EtherType.ARP:
                raise NetworkError("ARP frames should not reach this layer...")
            elif frame.ether_type == EtherType.IPV4:
                ip_payload = self.extract_ipv4_payload(frame)
                return ip_payload
            else:
                raise NotImplementedError(f"Ether type {frame.ether_type} not yet supported")  # TODO: implement ipv6
        else:
            self.say("Unsupported frame received, dropping it.")
            return None

    def extract_ipv4_payload(self, frame: EthernetFrame) -> bytes:
        try:
            packet = ipv4_packet_decoder(frame.payload)
            self.say(f"Received from {packet.source} the following packet payload:\n    > {packet.payload}")
            return packet
        except ValueError as e:
            self.say(f"Error while decoding packet inside frame from {frame.source}, it will be dropped. Cause:", e)

    def process_hdlc_frame(self, frame: HdlcFrame) -> Optional[bytes]:
        if not isinstance(frame, HdlcFrame):
            raise NetworkError("Expected to receive an HDLC frame on an HDLC interface")
        self.say("Received HDLC frame, extracting payload...")
        return frame.information

    def process_ppp_frame(self, frame: PppFrame) -> Optional[bytes]:
        if not isinstance(frame, PppFrame):
            raise NetworkError("Expected to receive an PPP frame on an PPP interface")
        self.say("Received PPP frame, extracting payload...")
        return frame.information







