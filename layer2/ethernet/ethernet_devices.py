from __future__ import annotations

import os
from typing import Callable, Optional

from layer2.ethernet.ethernet import EthernetFrame
from layer2.mac import Mac, UNKNOWN_MAC


class NetworkError(Exception):
    pass


class NetworkInterfaceCard(object):
    def __init__(self, mac: Mac, receive_callback: Callable[[Mac, Mac, object], None]):
        self.mac = mac
        self.cache: dict[Mac, NetworkInterfaceCard] = {}  # TODO: a nic doesn't have a cache, might be in software
        self.receive_callback = receive_callback
        self.default: Optional[NetworkInterfaceCard] = None

    def connect_to(self, nic: NetworkInterfaceCard):
        self.cache[nic.mac] = nic
        nic.cache[self.mac] = self

    def set_default(self, nic: NetworkInterfaceCard):
        if nic.mac not in self.cache:
            raise NetworkError(f"Can't set a NIC as default if it's not connected to this.")
        else:
            self.default = nic

    def send(self, source: Mac, target: Mac, data):
        if self.mac == target:
            self.receive_callback(self.mac, target, data)
        elif target in self.cache:
            self.cache[target].receive_callback(source, target, data)
        elif self.default is not None:
            self.default.receive_callback(source, target, data)
        else:
            raise NetworkError(f"Target {target} not found, and no default connection was set on NIC {self.mac}.")

    def disconnect_from(self, nic: NetworkInterfaceCard):
        self.cache.pop(nic.mac, None)
        nic.cache.pop(self.mac, None)
        if self.default == nic:
            self.default = None


# TODO: merge this into one with Ethernet Endpoint
class DeviceWithNic(object):
    def __init__(self,
                 receive_callback: Callable[[Mac, Mac, object], None],
                 mac: Mac = None,
                 short_name: str = "NO_NAME"):
        if mac is None:
            mac = Mac(os.urandom(6))
        self.nic = NetworkInterfaceCard(mac, receive_callback)
        self.short_name = short_name

    def say(self, string: str):
        print(f"[{self.short_name} ({self.nic.mac})]: {string}")

    def connect_to(self, other: DeviceWithNic, set_default=False):
        self.nic.connect_to(other.nic)
        self.say(f"Connected {self.nic.mac} to {other.nic.mac}")
        if set_default:
            self.set_default(other)

    def set_default(self, other: DeviceWithNic):
        self.nic.set_default(other.nic)
        self.say(f"Set {other.nic.mac} as default output.")

    def disconnect(self, other: DeviceWithNic):
        self.say(f"Disconnecting from {other}")
        self.nic.disconnect_from(other.nic)

    def __str__(self):
        return f"{self.short_name} ({self.nic.mac})"


# This is actually not how a switch works... A switch is more "dumb". A switch simply consists of interfaces, i.e.
# physical ports, and it keeps a cache/table of the mac addresses that are connected via those interfaces. Then,
# whenever it receives an ethernet frame and it recognizes the mac address, it will send the frame via the associated
# interface, or else it will flood all interfaces (except for the one sending the frame) with the frame.
#
# Shouldn't model it as a collection of NICs, because it doesnt have a mac (right?).
class EthernetSwitch(DeviceWithNic):
    def __init__(self, mac: Mac = None, short_name: str = ""):
        super().__init__(self.forward, mac, "SWITCH" + short_name)

    def forward(self, source: Mac, target, data):
        if self.nic.mac == target:
            self.say(f"Received from {source} the following data: '{data}'")
        elif target in self.nic.cache:
            self.say(f"Forwarding data from {source} to {target}")
            self.nic.cache[target].receive_callback(source, target, data)
        else:
            self.say(f"Unknown target {target}, sending to all")  # TODO: exclude the sending host
            self.broadcast_to_all(source, target, data)

    def broadcast_to_all(self, source, target, data):
        for others in self.nic.cache.values():
            others.receive_callback(source, target, data)


class EthernetEndpoint(DeviceWithNic):
    def __init__(self, mac: Mac = None, short_name: str = ""):
        super().__init__(self.receive, mac, "COMPUTER" + short_name)
        self.connected = False

    def receive(self, source: Mac, target: Mac, data):
        if not self.nic.mac == target:
            self.say(f"Dropping received frame addressed at {target}...")
        else:
            self.say(f"Received from {source} the following data:\n  > {data}")

    def send(self, target: Mac, data):
        self.nic.send(self.nic.mac, target, data)

    def send_frame(self, frame: EthernetFrame):
        if frame.source != self.nic.mac:
            raise ValueError(f"Invalid source specified in frame, expected {self.nic.mac} but was {frame.source}")
        self.send(frame.destination, frame)

    def connect_to(self, other: DeviceWithNic, **kwargs):
        if self.connected:
            raise NetworkError(f"This computer {self} only has one available connection, which is in use.")
        else:
            super().connect_to(other, set_default=True) # TODO: switch is not actually the default, should be router?
            self.connected = True

