from ipaddress import IPv4Network, ip_network, IPv6Network, IPv4Address, IPv6Address
from typing import TypeVar, Generic, List

from layer3.trie.trie import AbstractGenericTrie

V = TypeVar('V')


class IPv4RoutingTable(Generic[V], AbstractGenericTrie[IPv4Network, List[int], V]):
    def __init__(self, root_value: V = None):
        super().__init__(root_value)

    @staticmethod
    def pre_processor(key: IPv4Network | IPv4Address) -> List[int]:
        # if isinstance(key, List):
        #     return key
        if isinstance(key, IPv4Network):
            return network_to_bits(key, 32)
        return address_to_bits(key, 32)

    @staticmethod
    def post_processor(internal_key: List[int]) -> IPv4Network:
        return to_network4(internal_key)


class IPv6RoutingTable(Generic[V], AbstractGenericTrie[IPv6Network, List[int], V]):
    def __init__(self, root_value: V = None):
        super().__init__(root_value)

    @staticmethod
    def pre_processor(key: IPv6Network | IPv6Address) -> List[int]:
        if isinstance(key, IPv6Network):
            return network_to_bits(key, 128)
        return address_to_bits(key, 128)

    @staticmethod
    def post_processor(internal_key: List[int]) -> IPv6Network:
        return to_network6(internal_key)


def network_to_bits(network: IPv4Network | IPv6Network, num_bits: int):
    return address_to_bits(network.network_address, num_bits, network.prefixlen)


def address_to_bits(network: IPv4Address | IPv6Address, num_bits: int, prefixlen=None):
    if prefixlen is None:
        prefixlen = num_bits
    address = int(network)
    bits = []
    for k in range(num_bits - 1, num_bits - prefixlen - 1, -1):
        bits.append((address >> k) & 1)
    return bits


def to_network4(address_bits: List[int]):
    address, prefix_len = prefix_to_int(address_bits, num_bits=32)
    return IPv4Network(address=(address, prefix_len))


def to_network6(address_bits: List[int]):
    address, prefix_len = prefix_to_int(address_bits, num_bits=128)
    return IPv6Network(address=(address, prefix_len))


def prefix_to_int(prefix: List[int], num_bits: int) -> tuple[int, int]:
    bits = [0] * num_bits
    prefixlen = len(prefix)
    bits[:len(prefix)] = prefix
    address = reversed_bits_to_int(bits)
    return address, prefixlen


def reversed_bits_to_int(bits: List[int]) -> int:
    n = 0
    for bit in bits:
        n = (n << 1) | bit
    return n
