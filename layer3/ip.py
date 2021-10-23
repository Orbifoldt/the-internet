from __future__ import annotations

import ipaddress

from layer2.infrastructure.network_interface import NetworkInterface
from layer3.trie import trie

ipaddress.ip_address('192.168.0.1')
ipaddress.IPv4Address('192.168.0.1')

ipaddress.ip_address('2001:db8::')
ipaddress.IPv6Address('2001:db8::')


class ForwardingTable(object):
    def __init__(self):
        self.table: dict[ipaddress.IPv6Network | ipaddress.IPv4Network, NetworkInterface] = {}


