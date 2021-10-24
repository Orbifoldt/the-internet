from ipaddress import IPv4Address

from layer2.infrastructure.network_interface import DeviceWithInterfaces
from layer3.trie.routing_table import IPv4RoutingTable, IPv6RoutingTable


class IpRouter(DeviceWithInterfaces):

    def __init__(self, num_interfaces: int, name: str):
        super().__init__(num_interfaces, name, name_prefix="ROUTER")
        self.forwarding_table_v4: IPv4RoutingTable[int] = IPv4RoutingTable()
        self.forwarding_table_v6: IPv6RoutingTable[int] = IPv6RoutingTable()

    def forward(self, target: IPv4Address, data):
        network = self.forwarding_table_v4.find_best_match(target)
        interface_num = self.forwarding_table_v4[network]
        self.get_interface(interface_num).send(target, data)

    def receive(self, incoming_interface_num: int, **kwargs) -> None:
        self.say(*kwargs.values())
        self.forward(kwargs["target"], kwargs["data"])
