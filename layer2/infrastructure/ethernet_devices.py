from __future__ import annotations

from abc import ABC
from ipaddress import IPv4Address
from typing import Optional, List

from layer2.arp.arp import ARPPacket
from layer2.ethernet.ethernet import EthernetFrameBase, EtherType, EthernetFrame, LlcType, Ethernet802_3Frame
from layer2.infrastructure.network_error import NetworkError
from layer2.infrastructure.network_interface import EthernetInterface, DeviceWithInterfaces, EthernetInterfaceWithArp
from layer2.mac import Mac


class DeviceWithEthernetInterfaces(DeviceWithInterfaces, ABC):
    def __init__(self, num_interfaces: int, name: str = None, name_prefix: str = "eth", name_suffix: str = "",
                 mac: Mac = Mac()):
        super().__init__(num_interfaces, name, name_prefix, name_suffix)
        self._interfaces: List[EthernetInterface] = [EthernetInterface(i, self, mac) for i in range(num_interfaces)]
        self.mac = mac

    def get_interface(self, interface_num: int) -> EthernetInterface:
        return super().get_interface(interface_num)


class EthernetSwitch(DeviceWithEthernetInterfaces):
    def __init__(self, num_interfaces, name: Optional[str] = None, mac: Mac = Mac()):
        super().__init__(num_interfaces, name, name_prefix="SWITCH", mac=mac)
        self.cache: dict[Mac, EthernetInterface] = {}

    def receive(self, frame: EthernetFrameBase, incoming_interface_num: int) -> None:
        self.update_cache(frame.source, incoming_interface_num)
        self.forward(frame, incoming_interface_num)

    def send(self, frame: EthernetFrameBase, outgoing_interface_num: int) -> None:
        self.get_interface(outgoing_interface_num).send(frame)

    def forward(self, frame: EthernetFrameBase, incoming_interface_num):
        if frame.destination in self.cache:
            if self.cache[frame.destination].connector is None:
                self.say(f"No interface connected on {incoming_interface_num}, we'll just silently drop the frame.")
            else:
                self.say(f"Forwarding data from {frame.source}. Target {frame.destination} was cached "
                         f"on interface {self.cache[frame.destination].interface_num}")
                self.cache[frame.destination].send(frame=frame)
        else:
            self.say(f"Unknown target {frame.destination}, broadcasting frame to all")
            self.broadcast_to_all(frame, incoming_interface_num)

    def broadcast_to_all(self, frame: EthernetFrameBase, incoming_interface_num):
        for interface in self._interfaces:
            if interface.connector is not None and interface.interface_num != incoming_interface_num:
                self.say(
                    f"[eth_{interface.interface_num}]: Forwarding frame from {frame.source} to {frame.destination}")
                interface.send(frame=frame)

    def update_cache(self, source: Mac, port_num):
        self.cache[source] = self.get_interface(port_num)


class EthernetEndpoint(DeviceWithEthernetInterfaces):  # With a single interface in this case
    def __init__(self, mac: Mac = Mac(), name: str = None):
        super().__init__(1, name, name_prefix="COMPUTER", name_suffix=f" <{mac}>", mac=mac)

    def receive(self, frame: EthernetFrameBase, incoming_interface_num: int = 0):
        if self.mac == frame.destination:
            self.say(f"Received from {frame.source} the following frame data:\n    > {frame.payload}")
            return frame
        elif frame.destination == ARPPacket.UNKNOWN_MAC:
            self.say(f"Received possible ARP from {frame.source}, opening payload...")
            return frame
        else:
            self.say(f"Dropping received frame addressed at {frame.destination}...")

    def connect_to(self, device: DeviceWithEthernetInterfaces, other_interface_num: int, own_interface_num=0):
        super().connect_to(device, other_interface_num, own_interface_num=own_interface_num)

    def disconnect(self, own_interface_num=0):
        super().disconnect(interface_num=own_interface_num)

    def send(self, frame: EthernetFrameBase, outgoing_interface_num: int = 0):
        if frame.source != self.mac:
            raise NetworkError("Source MAC of the frame is not the same as self.mac")
        super().send(frame, outgoing_interface_num=outgoing_interface_num)

    def send_data(self, payload: bytes, destination: Mac, ether_type: EtherType = EtherType.IPV4):
        self.send(EthernetFrame(destination, self.mac, payload, ether_type))

    def send_data_802_3(self, payload: bytes, destination: Mac, ether_type: LlcType = LlcType.DEFAULT):
        self.send(Ethernet802_3Frame(destination, self.mac, payload, ether_type))


class DeviceWithArpEthernetInterfaces(DeviceWithInterfaces, ABC):
    def __init__(self, num_interfaces: int, ip_list: List[IPv4Address], name: str = None, name_prefix: str = "eth",
                 name_suffix: str = "", mac: Mac = Mac()):
        DeviceWithInterfaces.__init__(self, num_interfaces, name, name_prefix, name_suffix)
        self._interfaces = [EthernetInterfaceWithArp(i, self, ip_list[i], mac) for i in range(num_interfaces)]
        self.mac = mac

    def get_interface(self, interface_num: int) -> EthernetInterfaceWithArp:
        return super().get_interface(interface_num)


class EthernetEndpointWithArp(DeviceWithArpEthernetInterfaces, EthernetEndpoint):
    def __init__(self, ip4: IPv4Address, mac: Mac = Mac(), name: str = None):
        EthernetEndpoint.__init__(self, mac, name)
        DeviceWithArpEthernetInterfaces.__init__(self, num_interfaces=1, ip_list=[ip4], name=name,
                                                 name_prefix="COMPUTER", name_suffix=f" <{mac}>", mac=mac)
        self.get_interface(0).name = self.name + ": " + self.get_interface(0).name
