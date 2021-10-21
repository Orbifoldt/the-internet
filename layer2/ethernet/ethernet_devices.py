from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional

from layer2.mac import Mac, UNKNOWN_MAC


class NetworkError(Exception):
    pass


class NetworkInterface(object):
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces):
        self.connector: Optional[NetworkInterface] = None
        self.interface_num = interface_num
        self.parent: DeviceWithInterfaces = parent

    def receive(self, *args, **kwargs) -> None:
        self.parent.receive(*args, **kwargs)

    def send(self, source: Mac, target: Mac, data) -> None:
        if self.connector is None:
            raise NetworkError("No device connected to this interface")
        else:
            self.connector.receive(source, target, data, interface_num=self.interface_num)

    def connect(self, other_interface: NetworkInterface) -> None:
        if self.connector is not None:
            raise NetworkError("This interface is already connected")
        self.connector = other_interface
        if not other_interface.connector == self:
            other_interface.connect(self)

    def disconnect(self) -> None:
        other_connector = self.connector
        self.connector = None
        if other_connector.connector is not None:
            other_connector.disconnect()


class DeviceWithInterfaces(ABC):
    def __init__(self, num_interfaces: int, name: str):
        self.interfaces = [NetworkInterface(i, self) for i in range(num_interfaces)]
        self.name = name

    def get_interface(self, interface_num: int):
        if not 0 <= interface_num < len(self.interfaces):
            raise NetworkError(f"Device {self.name} has no interface with number {interface_num}")
        return self.interfaces[interface_num]

    @abstractmethod
    def receive(self, source: Mac, target: Mac, data, interface_num: int) -> None:  # TODO make this args+kwargs
        raise NotImplementedError

    # TODO create support for EthernetFrame
    def send(self, source: Mac, target: Mac, data, interface_num: int) -> None:  # TODO make this args+kwargs
        self.get_interface(interface_num).send(source, target, data)

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


class EthernetSwitch(DeviceWithInterfaces):
    def __init__(self, num_interfaces, name: Optional[str] = None):
        super().__init__(num_interfaces, f"SWITCH{'' if name is None else f'_{name}'}")
        self.cache = {}

    def receive(self, source, target, data, interface_num):
        self.forward(source, target, data, interface_num)
        self.update_cache(source, interface_num)

    def forward(self, source: Mac, target, data, port_num):
        if target in self.cache:
            self.say(f"Forwarding data from {source}. "
                     f"Target {target} was cached on interface {self.cache[target].interface_num}")
            self.cache[target].send(source, target, data)
        else:
            self.say(f"Unknown target {target}, broadcasting frame to all")
            self.broadcast_to_all(source, target, data, port_num)

    def broadcast_to_all(self, source, target, data, port_num):
        for interface in self.interfaces:
            if interface.connector is not None and interface.interface_num != port_num:
                print(f"[INTERFACE {interface.interface_num}]: Forwarding data from {source} to {target}")
                interface.send(source, target, data)

    def update_cache(self, source, port_num):
        self.cache[source] = self.interfaces[port_num]


class EthernetEndpoint(DeviceWithInterfaces):
    def __init__(self, mac: Mac, name: str = None):
        self.mac = mac
        super().__init__(1, f"COMPUTER{'' if name is None else f'_{name}'} ({self.mac})")

    def receive(self, source, target, data, **kwargs):
        if self.mac == target:
            self.say(f"Received from {source} the following data:\n  > {data}")
        else:
            self.say(f"Dropping received frame addressed at {target}...")

    def connect_to2(self, device: DeviceWithInterfaces, other_interface_num: int):
        self.connect_to(device, other_interface_num, own_interface_num=0)

    def disconnect2(self):
        self.disconnect(interface_num=0)

    def send2(self, target: Mac, data):
        self.send(self.mac, target, data, interface_num=0)
