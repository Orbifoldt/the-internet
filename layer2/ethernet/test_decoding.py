from unittest import TestCase

from layer2.ethernet.decoding import decode, decode_bytes
from layer2.ethernet.encoding import encode, encode_bytes
from layer2.ethernet.ethernet import EthernetFrame
from layer2.mac import Mac


class TestDecoding(TestCase):
    dest = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    src = Mac.fromstring("ff:11:aa:55:cc:99")

    def test_decode_multiple_frames(self):
        payload1 = b'This is some ASCII encoded text that we put into this ethernet frame'
        payload2 = b'This is some more ASCII text {}[]~0123456789'
        frame1 = EthernetFrame(self.dest, self.src, payload1)
        frame2 = EthernetFrame(self.dest, self.src, payload2)
        encoded = encode([frame1, frame2])

        decoded_frames = decode(encoded)
        self.assertEqual(2, len(decoded_frames))
        self.assertEqual(frame1, decoded_frames[0])
        self.assertEqual(frame2, decoded_frames[1])

    def test_decode_bytes_multiple_frames(self):
        payload1 = b'This is some ASCII encoded text that we put into this ethernet frame'
        payload2 = b'This is some more ASCII text {}[]~0123456789'
        frame1 = EthernetFrame(self.dest, self.src, payload1)
        frame2 = EthernetFrame(self.dest, self.src, payload2)
        encoded = encode_bytes([frame1, frame2])

        decoded_frames = decode_bytes(encoded)
        self.assertEqual(2, len(decoded_frames))
        self.assertEqual(frame1, decoded_frames[0])
        self.assertEqual(frame2, decoded_frames[1])
