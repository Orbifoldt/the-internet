from __future__ import annotations

from typing import Optional

from layer2.arp.arp import ARPPacket
from layer2.ethernet.ethernet import EthernetFrameBase, EtherType, EthernetFrame, LlcType, Ethernet802_3Frame
from layer2.infrastructure.network_error import NetworkError
from layer2.infrastructure.network_interface import DeviceWithInterfaces, NetworkInterface
from layer2.mac import Mac


class EthernetSwitch(DeviceWithInterfaces):
    def __init__(self, num_interfaces, name: Optional[str] = None):
        super().__init__(num_interfaces, name, name_prefix="SWITCH")
        self.cache: dict[Mac, NetworkInterface] = {}

    def receive(self, incoming_interface_num: int, **kwargs) -> None:
        frame: EthernetFrameBase = kwargs['frame']
        self.forward(frame, incoming_interface_num)
        self.update_cache(frame.source, incoming_interface_num)

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
        for interface in self.interfaces:
            if interface.connector is not None and interface.interface_num != incoming_interface_num:
                print(
                    f"[INTERFACE {interface.interface_num}]: Forwarding data from {frame.source} to {frame.destination}")
                interface.send(frame=frame)

    def update_cache(self, source: Mac, port_num):
        self.cache[source] = self.interfaces[port_num]


class EthernetEndpoint(DeviceWithInterfaces):  # With a single interface in this case
    def __init__(self, mac: Mac = None, name: str = None):
        if mac is None:
            mac = Mac()
        self.mac = mac
        super().__init__(1, name, name_prefix="COMPUTER", name_suffix=f" <{self.mac}>")

    def receive(self, incoming_interface_num: int = 0, **kwargs):
        frame: EthernetFrameBase = kwargs['frame']
        if self.mac == frame.destination:
            self.say(f"Received from {frame.source} the following frame data:\n    > {frame.payload}")
            return frame
        elif frame.destination == ARPPacket.UNKNOWN_MAC:
            self.say(f"Received possible ARP from {frame.source}, opening payload...")
            return frame

        else:
            self.say(f"Dropping received frame addressed at {frame.destination}...")

    def connect_to(self, device: DeviceWithInterfaces, other_interface_num: int, own_interface_num=0):
        super().connect_to(device, other_interface_num, own_interface_num=0)

    def disconnect(self, own_interface_num=0):
        super().disconnect(interface_num=0)

    def send(self, outgoing_interface_num: int = 0, **kwargs):
        frame: EthernetFrameBase = kwargs['frame']
        if frame.source != self.mac:
            raise NetworkError("Source MAC of the frame is not the same as self.mac")
        super().send(outgoing_interface_num=outgoing_interface_num, frame=frame)

    def send_frame(self, frame: EthernetFrameBase):
        self.send(frame=frame)

    def send_data(self, payload: bytes, destination: Mac, ether_type: EtherType = EtherType.IPV4):
        self.send_frame(EthernetFrame(destination, self.mac, payload, ether_type))

    def send_data_802_3(self, payload: bytes, destination: Mac, ether_type: LlcType = LlcType.DEFAULT):
        self.send_frame(Ethernet802_3Frame(destination, self.mac, payload, ether_type))


