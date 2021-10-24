from ipaddress import ip_network, ip_address
from unittest import TestCase

from layer3.trie.routing_table import network_to_bits, to_network4, to_network6, reversed_bits_to_int, prefix_to_int, \
    IPv4RoutingTable


class Test(TestCase):
    def test_reversed_bits_to_int(self):
        bits = [0, 1, 0, 1, 1]
        x = reversed_bits_to_int(bits)
        self.assertEqual(8 + 2 + 1, x)

    def test_network_to_bits_and_back_v4(self):
        network = ip_network('192.0.2.0/29')
        bits = network_to_bits(network, 32)
        result = to_network4(bits)
        self.assertEqual(network, result)

    def test_network_to_bits_and_back_v6(self):
        network = ip_network('2001:db00::0/24')
        bits = network_to_bits(network, 128)
        result = to_network6(bits)
        self.assertEqual(network, result)

    def test_prefix_to_int(self):
        network = ip_network('192.0.2.0/29')
        bits = network_to_bits(network, 32)
        x = prefix_to_int(bits, 32)
        self.assertEqual(int(network.network_address), x[0])
        self.assertEqual(network.prefixlen, x[1])

    def test_v4_routing_table(self):
        netw1 = ip_network('192.0.2.0/24')
        netw1_sub = ip_network('192.0.2.0/28')
        netw2 = ip_network('192.0.17.0/24')
        netw3 = ip_network('10.28.79.0/30')

        table = IPv4RoutingTable()
        table[netw1] = "netw1"
        table[netw1_sub] = "netw1_sub"
        table[netw2] = "netw2"
        table[netw3] = "netw3"

        addr1 = ip_address('192.0.2.217')
        addr1_sub = ip_address('192.0.2.7')
        addr2 = ip_address('192.0.17.33')
        addr3 = ip_address('10.28.79.1')

        self.assertEqual(netw1, table.find_best_match(addr1))
        self.assertEqual(netw1_sub, table.find_best_match(addr1_sub))
        self.assertEqual(netw2, table.find_best_match(addr2))
        self.assertEqual(netw3, table.find_best_match(addr3))

        addr_unknown = ip_address('35.15.68.155')
        with self.assertRaises(KeyError):
            _ = table[addr_unknown]

