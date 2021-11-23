from __future__ import annotations

from abc import abstractmethod, ABC
from ipaddress import IPv4Address
from typing import Optional

from layer2.arp.arp import extract_arp_packet, ARPOperation, ARPPacket, ARPFrame
from layer2.ethernet.decoding import decode_frame
from layer2.ethernet.ethernet import EthernetFrameBase, EthernetFrame, EtherType
from layer2.hdlc.hdlc import HdlcFrame
from layer2.infrastructure.network_error import NetworkError
from layer2.mac import Mac
from layer2.ppp.point_to_point import PppFrame


class NetworkInterface(object):
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces, name="interface"):
        self.connector: Optional[NetworkInterface] = None
        self.interface_num = interface_num
        self.parent: DeviceWithInterfaces = parent
        self.name = name + f"{interface_num}"

    def receive(self, data: bytes, incoming_interface_num: int) -> None:
        self.parent.receive(data, incoming_interface_num=incoming_interface_num)

    def send(self, data: bytes) -> None:
        if self.connector is None:
            raise NetworkError("No device connected to this interface")
        else:
            self.connector.receive(data, incoming_interface_num=self.connector.interface_num)

    def connect(self, other_interface: NetworkInterface) -> None:
        if self.connector is not None:
            raise NetworkError("This interface is already connected")
        self.connector = other_interface
        if not other_interface.connector == self:
            other_interface.connect(self)

    def disconnect(self) -> None:
        if self.connector is not None:
            other_connector = self.connector
            self.connector = None
            if other_connector.connector is not None:
                other_connector.disconnect()

    def __str__(self):
        return f"INTERFACE[interface_num={self.interface_num}, parent={self.parent}]"

    def say(self, *args):
        self.parent.say(f"<[{self.name}]>:", *args)


class DeviceWithInterfaces(ABC):
    def __init__(self, num_interfaces: int, name: str = None, name_prefix: str = "DEVICE", name_suffix: str = ""):
        self._interfaces = [NetworkInterface(i, self) for i in range(num_interfaces)]
        self.name = name_prefix + ('' if name is None else f'_{name}') + name_suffix

    def get_interface(self, interface_num: int):
        if not 0 <= interface_num < len(self._interfaces):
            raise NetworkError(f"Device {self.name} has no interface with number {interface_num}")
        return self._interfaces[interface_num]

    @abstractmethod
    def receive(self, data, incoming_interface_num: int) -> None:
        raise NotImplementedError

    def send(self, data, outgoing_interface_num: int) -> None:
        self.get_interface(outgoing_interface_num).send(data)

    def connect_to(self, device: DeviceWithInterfaces, other_interface_num: int, own_interface_num: int):
        own_interface = self.get_interface(own_interface_num)
        other_interface = device.get_interface(other_interface_num)
        own_interface.connect(other_interface)

    def disconnect(self, interface_num: int):
        self.get_interface(interface_num).disconnect()

    def say(self, *args):
        print(f"[{self.name}]:", *args)

    def __str__(self):
        return self.name


class EthernetInterface(NetworkInterface):
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces, mac: Mac = Mac(), ):
        super().__init__(interface_num, parent, name="eth")
        self._mac = mac

    @property
    def mac(self):
        return self._mac

    def receive(self, data: bytes, incoming_interface_num: int) -> None:
        frame = decode_frame(data)
        self.parent.receive(frame, incoming_interface_num=incoming_interface_num)

    def send(self, frame: EthernetFrameBase) -> None:
        raw_data = frame.bytes()
        super().send(raw_data)

    def connect(self, other_interface: EthernetInterface) -> None:
        if not isinstance(other_interface, EthernetInterface):
            raise NetworkError("Cannot connect to a non-ethernet interface")
        super().connect(other_interface)


class HdlcInterface(NetworkInterface):  # TODO This needs an ip address when using with IP (or make it ip unnumbered)
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces, extended: bool = False):
        super().__init__(interface_num, parent, name="hdlc")
        self.extended = extended

    def receive(self, data: bytes, incoming_interface_num: int) -> None:
        frame = HdlcFrame.decode_frame_from_bytes(data, extended=self.extended)
        self.parent.receive(frame, incoming_interface_num=incoming_interface_num)

    def send(self, frame: HdlcFrame) -> None:
        raw_data = frame.bytes()
        super().send(raw_data)

    def connect(self, other_interface: HdlcInterface) -> None:
        if not isinstance(other_interface, HdlcInterface):
            raise NetworkError("Cannot connect to a non-HDLC interface")
        super().connect(other_interface)


class PppInterface(NetworkInterface):  # TODO This needs an ip address when using with IP (or make it ip unnumbered)
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces):
        super().__init__(interface_num, parent, name="ppp")

    def receive(self, data: bytes, incoming_interface_num: int) -> None:
        frame = PppFrame.decode_ppp_frame_from_bytes(data)
        self.parent.receive(frame, incoming_interface_num=incoming_interface_num)

    def send(self, frame: PppFrame) -> None:
        raw_data = frame.bytes()
        super().send(raw_data)

    def connect(self, other_interface: PppInterface) -> None:
        if not isinstance(other_interface, PppInterface):
            raise NetworkError("Cannot connect to a non-PPP interface")
        super().connect(other_interface)


class EthernetInterfaceWithArp(EthernetInterface):
    """
    Ethernet interface that automatically handles ARP requests, so only non-ARP frames are forwarded to the parent.
    """
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces, ip4: IPv4Address, mac: Mac = Mac()):
        super().__init__(interface_num, parent, mac)
        self.ip4_cache: dict[IPv4Address, Mac] = {}
        self.ip4 = ip4

    def receive(self, data: bytes, incoming_interface_num: int) -> None:
        frame = self.process_ethernet_frame(decode_frame(data))
        if frame is not None:
            self.parent.receive(frame, incoming_interface_num=incoming_interface_num)

    def process_ethernet_frame(self, frame: EthernetFrameBase) -> Optional[EthernetFrameBase]:
        if not isinstance(frame, EthernetFrameBase):
            raise NetworkError("Expected to receive an ethernet frame on an ethernet interface")

        if isinstance(frame, EthernetFrame):
            if frame.ether_type == EtherType.ARP:
                self.process_arp(frame)
                return None
        return frame

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
        self.send(response)

    def send_arp_for(self, other_ip: IPv4Address):
        """ Send out an ARP request for the other_ip address to discover and store their mac address """
        arp_frame = ARPFrame(ARPPacket(self.mac, self.ip4, other_ip))
        self.send(arp_frame)
