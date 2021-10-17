from unittest import TestCase

from layer2.ethernet.encoding import encode, encode_bytes
from layer2.ethernet.ethernet import EthernetFrame
from layer2.mac import Mac


class TestEncoding(TestCase):
    dest = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    src = Mac.fromstring("ff:11:aa:55:cc:99")

    def test_encode_multiple_frames(self):
        payload1 = b'This is some ASCII encoded text that we put into this ethernet frame'
        payload2 = b'This is some more ASCII text {}[]~0123456789'
        frame1 = EthernetFrame(self.dest, self.src, payload1)
        frame2 = EthernetFrame(self.dest, self.src, payload2)

        encoded = [b for b in encode([frame1, frame2])]
        expected = [None] * 96 + [b for b in frame1.phys_bits()] + [None] * 96 + [b for b in frame2.phys_bits()] + \
                   [None] * 96
        self.assertEqual(expected, encoded)

    def test_encode_multiple_frames_to_bytes(self):
        payload1 = b'This is some ASCII encoded text that we put into this ethernet frame'
        payload2 = b'This is some more ASCII text {}[]~0123456789'
        frame1 = EthernetFrame(self.dest, self.src, payload1)
        frame2 = EthernetFrame(self.dest, self.src, payload2)

        # encoded = [b for b in encode_bytes([frame1, frame2])]
        encoded = encode_bytes([frame1, frame2])
        expected = [None] * 12 + [b for b in frame1.phys_bytes()] + [None] * 12 + [b for b in frame2.phys_bytes()] + \
                   [None] * 12
        self.assertEqual(expected, encoded)
