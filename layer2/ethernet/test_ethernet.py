from unittest import TestCase
from ethernet import *


class TestEthernetFrame(TestCase):
    dest = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    src = Mac.fromstring("ff:11:aa:55:cc:99")

    def test_create_frame(self):
        payload = b'This is some ASCII encoded text that we put into this ethernet frame'
        frame = EthernetFrame(self.dest, self.src, payload)

        expected = "a1b2c3d4e5f6" \
                   "ff11aa55cc99" \
                   "0800" \
                   "5468697320697320736f6d6520415343494920656e636f64656420746578742074686174207765207075742" \
                   "0696e746f20746869732065746865726e6574206672616d65" \
                   "e9d10d2b"  # The crc32 checksum (bytes reversed)
        self.assertEqual(frame.bits(), BitArray(hex="0x" + expected))

    def test_create_frame_small_payload_is_padded(self):
        payload = b'This is payload'
        frame = EthernetFrame(self.dest, self.src, payload)

        expected = "a1b2c3d4e5f6" \
                   "ff11aa55cc99" \
                   "0800" \
                   "54686973206973207061796c6f616400000000000000000000000000000000000000000000000000000000000000" \
                   "e4544c44"  # The crc32 checksum (bytes reversed)
        self.assertEqual(frame.bits(), BitArray(hex="0x" + expected))

    def test_create_frame_too_large_payload_should_raise_value_error(self):
        payload = b'Payload is way too large' * 500
        with self.assertRaises(ValueError):
            EthernetFrame(self.dest, self.src, payload)
