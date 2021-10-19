from unittest import TestCase

from ethernet_devices import EthernetEndpoint, EthernetSwitch, NetworkError
from layer2.mac import Mac, UNKNOWN_MAC


class TestNetworkInterface(TestCase):
    macA = Mac.fromstring("AA:AA:AA:AA:AA:AA")
    macB = Mac.fromstring("BB:BB:BB:BB:BB:BB")
    mac_switch = Mac.fromstring("11:11:11:11:11:11")

    def test_networking(self):
        macA = Mac.fromstring("AA:AA:AA:AA:AA:AA")
        macB = Mac.fromstring("BB:BB:BB:BB:BB:BB")
        macC = UNKNOWN_MAC
        mac_switch = Mac.fromstring("11:11:11:11:11:11")
        computerA = EthernetEndpoint(macA, "_A")
        computerB = EthernetEndpoint(macB, "_B")
        switch = EthernetSwitch(mac_switch)

        print(f"\nWe'll connect {computerA} and {computerB} each to the switch {switch}.")
        computerA.connect_to(switch)
        computerB.connect_to(switch)

        print(f"\nThen we'll send some data between {computerA} and {computerB} via our switch {switch}.")
        computerA.send(macB, "Hello there Bob!")
        computerB.send(macA, "Hello back to you Alice!")

        print(f"\nIf {computerA} sends some frame to unknown destination it won't be received.")
        computerA.send(macC, "Non-existing mac should not receive this data")

        print(f"\nNow {computerB} disconnects from the switch.")
        computerB.disconnect(switch)

        print(f"\nIf then {computerA} tries to send something to {computerB} we get:")
        computerA.send(macB, "Oh no, it seems B disconnected")

    def test_ethernet_endpoint_cant_have_multiple_connections(self):
        computerA = EthernetEndpoint(self.macA, "_A")
        computerB = EthernetEndpoint(self.macB, "_B")
        switch = EthernetSwitch(self.mac_switch)

        computerA.connect_to(switch)
        with self.assertRaises(NetworkError):
            computerA.connect_to(computerB)


