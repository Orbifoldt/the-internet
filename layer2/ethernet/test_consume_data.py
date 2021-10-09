from unittest import TestCase

from layer1.manchester_encoding import encode
from layer2.ethernet.consume_data import ethernet_frame_from
from layer2.ethernet.ethernet import EthernetFrame
from layer2.mac import Mac


class Test(TestCase):
    dest = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    src = Mac.fromstring("ff:11:aa:55:cc:99")
    payload = b'This is some ASCII encoded text that we put into this ethernet frame'
    frame = EthernetFrame(dest, src, payload)

    def test_ethernet_frame_from_phys_signal_should_extract_all_information(self):
        phys_signal = encode(self.frame.phys_bits())

        decoded_frame = ethernet_frame_from(phys_signal)

        self.assertEqual(self.dest, decoded_frame.destination)
        self.assertEqual(self.src, decoded_frame.source)
        self.assertEqual(self.payload, decoded_frame.payload)
        self.assertEqual(bytes.fromhex("e9d10d2b"), decoded_frame.fcs)

    def test_corrupted_frame_should_raise_value_error(self):
        corrupted_bits = self.frame.phys_bits()
        corrupted_bits.set(not corrupted_bits[99], 99)  # flip a bit
        phys_signal = encode(corrupted_bits)

        with self.assertRaises(ValueError):
            ethernet_frame_from(phys_signal)
