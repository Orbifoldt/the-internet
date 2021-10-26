from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional

from layer2.infrastructure.network_error import NetworkError


class NetworkInterface(object):
    def __init__(self, interface_num: int, parent: DeviceWithInterfaces):
        self.connector: Optional[NetworkInterface] = None
        self.interface_num = interface_num
        self.parent: DeviceWithInterfaces = parent

    def receive(self, **kwargs) -> None:
        self.parent.receive(**kwargs)

    def send(self, **kwargs) -> None:
        if self.connector is None:
            raise NetworkError("No device connected to this interface")
        else:
            self.connector.receive(incoming_interface_num=self.connector.interface_num, **kwargs)

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


class DeviceWithInterfaces(ABC):
    def __init__(self, num_interfaces: int, name: str = None, name_prefix: str = "DEVICE", name_suffix: str = ""):
        self.interfaces = [NetworkInterface(i, self) for i in range(num_interfaces)]
        self.name = name_prefix + ('' if name is None else f'_{name}') + name_suffix

    def get_interface(self, interface_num: int):
        if not 0 <= interface_num < len(self.interfaces):
            raise NetworkError(f"Device {self.name} has no interface with number {interface_num}")
        return self.interfaces[interface_num]

    @abstractmethod
    def receive(self, incoming_interface_num: int, **kwargs) -> None:
        raise NotImplementedError

    def send(self, outgoing_interface_num: int, **kwargs) -> None:
        self.get_interface(outgoing_interface_num).send(**kwargs)

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
