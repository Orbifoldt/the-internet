from layer2.infrastructure.network_interface import DeviceWithInterfaces
from layer3.ip.ipv4 import IPv4Packet
from layer3.trie.routing_table import IPv4RoutingTable, IPv6RoutingTable


class IpRouter(DeviceWithInterfaces):  # Maybe extend switch instead?

    def __init__(self, num_interfaces: int, name: str):
        super().__init__(num_interfaces, name, name_prefix="ROUTER")
        self.forwarding_table_v4: IPv4RoutingTable[int] = IPv4RoutingTable()
        self.forwarding_table_v6: IPv6RoutingTable[int] = IPv6RoutingTable()

    def forward(self, packet: IPv4Packet):  # TODO: be able to receive bytes? or just both ipv4 and ipv6
        network = self.forwarding_table_v4.find_best_match(packet.destination)
        interface_num = self.forwarding_table_v4[network]
        packet.decrease_ttl()
        self.get_interface(interface_num).send(packet)

    def receive(self, incoming_interface_num: int, **kwargs) -> None:
        self.say(*kwargs.values())
        self.forward(kwargs["packet"])
