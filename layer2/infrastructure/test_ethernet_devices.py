from unittest import TestCase

from layer2.infrastructure.ethernet_devices import EthernetEndpoint, EthernetSwitch
from layer2.infrastructure.network_error import NetworkError
from layer2.mac import Mac, UNKNOWN_MAC


class TestNetworkInterface(TestCase):
    macA = Mac.fromstring("AA:AA:AA:AA:AA:AA")
    macB = Mac.fromstring("BB:BB:BB:BB:BB:BB")
    computer_A = EthernetEndpoint(macA, "A")
    computer_B = EthernetEndpoint(macB, "B")
    
    def tearDown(self) -> None:
        self.computer_A.disconnect()
        self.computer_B.disconnect()

    def test_networking(self):
        macC = UNKNOWN_MAC
        switch = EthernetSwitch(3)

        print(f"\nWe'll connect {self.computer_A} and {self.computer_B} each to the switch {switch}.")
        self.computer_A.connect_to(switch, 0)
        self.computer_B.connect_to(switch, 1)

        print(f"\nThen we'll send some data between {self.computer_A} and {self.computer_B} via our switch {switch}.")
        self.computer_A.send_data(b"Hello there Bob!", self.macB)
        print("----------------------------------------")
        self.computer_B.send_data(b"Hello back to you Alice!", self.macA)

        print(f"\nIf {self.computer_A} sends some frame to unknown destination it won't be received.")
        self.computer_A.send_data(b"Non-existing mac should not receive this data", macC)

        print(f"\nNow {self.computer_B} disconnects from the switch.")
        self.computer_B.disconnect()

        print(f"\nIf then {self.computer_A} tries to send something to {self.computer_B} we get:")
        self.computer_A.send_data(b"Oh no, it seems B disconnected", self.macB)

    def test_sending_data_to_a_switch_will_update_its_cache_to_keep_track_of_interface_number(self):
        switch = EthernetSwitch(3)

        self.computer_A.connect_to(switch, 0)
        self.computer_B.connect_to(switch, 1)

        self.computer_B.send_data(b"Hello there Alice!", self.macA)
        self.computer_A.send_data(b"Hello back at you Bob!", self.macB)

        self.assertEqual(0, switch.cache[self.macA].interface_num)
        self.assertEqual(1, switch.cache[self.macB].interface_num)
        self.assertEqual(2, len(switch.cache))

    def test_reconnecting_will_properly_update_switch_cache(self):
        switch = EthernetSwitch(5)

        self.computer_A.connect_to(switch, 4)
        self.computer_A.send_data(b"Some data", self.macB)

        self.assertEqual(4, switch.cache[self.macA].interface_num)

        self.computer_A.disconnect()
        self.computer_A.connect_to(switch, 3)
        self.computer_A.send_data(b"Some data", self.macB)

        self.assertEqual(3, switch.cache[self.macA].interface_num)
        self.assertEqual(1, len(switch.cache))

    def test_ethernet_endpoint_can_only_have_single_connection(self):
        switch = EthernetSwitch(7)

        self.computer_A.connect_to(switch, 0)
        with self.assertRaises(NetworkError):
            self.computer_A.connect_to(self.computer_B, 0)

    def test_switch_can_only_have_single_connection_on_one_interface(self):
        switch = EthernetSwitch(7)

        self.computer_A.connect_to(switch, 0)
        with self.assertRaises(NetworkError):
            self.computer_B.connect_to(switch, 0)

    def test_can_connect_to_other_after_disconnecting(self):
        switch = EthernetSwitch(7)

        self.computer_A.connect_to(switch, 0)
        self.computer_A.disconnect()
        self.computer_A.connect_to(self.computer_B, 0)

        self.assertEqual(self.computer_A.get_interface(0), self.computer_B.get_interface(0).connector)


