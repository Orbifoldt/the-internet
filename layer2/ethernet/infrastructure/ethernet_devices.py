from __future__ import annotations

from typing import Optional

from layer2.ethernet.ethernet import EthernetFrameBase, EtherType, EthernetFrame, LlcType, Ethernet802_3Frame
from layer2.ethernet.infrastructure.network_error import NetworkError
from layer2.ethernet.infrastructure.network_interface import DeviceWithInterfaces, NetworkInterface
from layer2.mac import Mac


class EthernetSwitch(DeviceWithInterfaces):
    def __init__(self, num_interfaces, name: Optional[str] = None):
        super().__init__(num_interfaces, name, name_prefix="SWITCH")
        self.cache: dict[Mac, NetworkInterface] = {}

    def receive(self, frame: EthernetFrameBase, interface_num: int, **kwargs) -> None:
        self.forward(frame, interface_num)
        self.update_cache(frame.source, interface_num)

    def forward(self, frame: EthernetFrameBase, port_num):
        if frame.destination in self.cache:
            if self.cache[frame.destination].connector is None:
                self.say(f"No interface connected on {port_num}, we'll just act as if we sent the frame...")
            else:
                self.say(f"Forwarding data from {frame.source}. Target {frame.destination} was cached "
                         f"on interface {self.cache[frame.destination].interface_num}")
                self.cache[frame.destination].send(frame)
        else:
            self.say(f"Unknown target {frame.destination}, broadcasting frame to all")
            self.broadcast_to_all(frame, port_num)

    def broadcast_to_all(self, frame: EthernetFrameBase, port_num):
        for interface in self.interfaces:
            if interface.connector is not None and interface.interface_num != port_num:
                print(f"[INTERFACE {interface.interface_num}]: Forwarding data from {frame.source} to {frame.destination}")
                interface.send(frame)

    def update_cache(self, source: Mac, port_num):
        self.cache[source] = self.interfaces[port_num]


class EthernetEndpoint(DeviceWithInterfaces):
    def __init__(self, mac: Mac = None, name: str = None):
        if mac is None:
            mac = Mac()
        self.mac = mac
        super().__init__(1, name, name_prefix="COMPUTER", name_suffix=f" ({self.mac})")

    def receive(self, frame: EthernetFrameBase, **kwargs):
        if self.mac == frame.destination:
            self.say(f"Received from {frame.source} the following data:\n  > {frame.payload}")
            if 'callback' in kwargs:
                kwargs['callback']()
        else:
            self.say(f"Dropping received frame addressed at {frame.destination}...")

    def connect_to(self, device: DeviceWithInterfaces, other_interface_num: int, own_interface_num=0):
        super().connect_to(device, other_interface_num, own_interface_num=0)

    def disconnect(self, own_interface_num=0):
        super().disconnect(interface_num=0)

    def send(self, frame: EthernetFrameBase, **kwargs):
        if frame.source != self.mac:
            raise NetworkError("Source MAC of the frame is not the same as self.mac")
        super().send(frame, interface_num=0)

    def send_data(self, payload: bytes, destination: Mac, ether_type: EtherType = EtherType.IPV4):
        self.send(EthernetFrame(destination, self.mac, payload, ether_type))

    def send_data_802_3(self, payload: bytes, destination: Mac, ether_type: LlcType = LlcType.DEFAULT):
        self.send(Ethernet802_3Frame(destination, self.mac, payload, ether_type))

