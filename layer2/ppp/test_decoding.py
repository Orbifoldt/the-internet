from unittest import TestCase

from layer2.frame import encode, encode_bytes, decode, decode_bytes
from layer2.hdlc_base import HdlcMode
from layer2.ppp.point_to_point import PppFrame, PppProtocol


class TestDecoding(TestCase):
    information = b'Some information[] that{} we~# send in this frame!'
    ppp_frame = PppFrame(PppProtocol.IPv4, information)

    def test_encode_async_mode(self):
        encoded = encode([self.ppp_frame], HdlcMode.ASYNC)
        decoded = decode(encoded, PppFrame, mode=HdlcMode.ASYNC)
        self.assertEqual([self.ppp_frame], decoded)

    def test_encode_bytes_async_mode(self):
        encoded = encode_bytes([self.ppp_frame], HdlcMode.ASYNC)
        decoded = decode_bytes(encoded, PppFrame, mode=HdlcMode.ASYNC)
        self.assertEqual([self.ppp_frame], decoded)

