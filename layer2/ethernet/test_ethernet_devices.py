from unittest import TestCase

from ethernet_devices import NetworkError, EthernetEndpoint, EthernetSwitch
from layer2.mac import Mac, UNKNOWN_MAC


class TestNetworkInterface(TestCase):
    macA = Mac.fromstring("AA:AA:AA:AA:AA:AA")
    macB = Mac.fromstring("BB:BB:BB:BB:BB:BB")
    mac_switch = Mac.fromstring("11:11:11:11:11:11")

    def test_networking(self):
        macA = Mac.fromstring("AA:AA:AA:AA:AA:AA")
        macB = Mac.fromstring("BB:BB:BB:BB:BB:BB")
        macC = UNKNOWN_MAC
        computerA = EthernetEndpoint(macA, "A")
        computerB = EthernetEndpoint(macB, "B")
        switch = EthernetSwitch(3)

        print(f"\nWe'll connect {computerA} and {computerB} each to the switch {switch}.")
        computerA.connect_to2(switch, 0)
        computerB.connect_to2(switch, 1)

        print(f"\nThen we'll send some data between {computerA} and {computerB} via our switch {switch}.")
        computerA.send2(macB, "Hello there Bob!")
        print("----------------------------------------")
        computerB.send2(macA, "Hello back to you Alice!")

        print(f"\nIf {computerA} sends some frame to unknown destination it won't be received.")
        computerA.send2(macC, "Non-existing mac should not receive this data")

        print(f"\nNow {computerB} disconnects from the switch.")
        computerB.disconnect2()

        print(f"\nIf then {computerA} tries to send something to {computerB} we get:")
        computerA.send2(macB, "Oh no, it seems B disconnected")

    def test_ethernet_endpoint_can_only_have_single_connection(self):
        computerA = EthernetEndpoint(self.macA, "A")
        computerB = EthernetEndpoint(self.macB, "B")
        switch = EthernetSwitch(7)

        computerA.connect_to2(switch, 0)
        with self.assertRaises(NetworkError):
            computerA.connect_to2(computerB, 0)

    def test_switch_can_only_have_single_connection_on_one_interface(self):
        computerA = EthernetEndpoint(self.macA, "A")
        computerB = EthernetEndpoint(self.macB, "B")
        switch = EthernetSwitch(7)

        computerA.connect_to2(switch, 0)
        with self.assertRaises(NetworkError):
            computerB.connect_to2(switch, 0)

    def test_can_connect_to_other_after_disconnecting(self):
        computerA = EthernetEndpoint(self.macA, "A")
        computerB = EthernetEndpoint(self.macB, "B")
        switch = EthernetSwitch(7)

        computerA.connect_to2(switch, 0)
        computerA.disconnect2()
        computerA.connect_to2(computerB, 0)

        self.assertEqual(computerA.get_interface(0), computerB.get_interface(0).connector)


