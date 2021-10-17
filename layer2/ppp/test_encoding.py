from unittest import TestCase

from bitstring import BitArray

from layer2.frame import encode, encode_bytes
from layer2.hdlc_base import HdlcMode, HdlcLikeBaseFrame
from layer2.ppp.point_to_point import PppFrame, PppProtocol


class TestEncoding(TestCase):
    information = b'Some information that we send in this frame!'
    ppp_frame = PppFrame(PppProtocol.IPv4, information)

    def test_encode_async_mode(self):
        flag = HdlcLikeBaseFrame.flag
        encoded = encode([self.ppp_frame], HdlcMode.ASYNC)
        expected = BitArray(auto=flag + self.ppp_frame.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_bytes_async_mode(self):
        flag = HdlcLikeBaseFrame.flag
        encoded = encode_bytes([self.ppp_frame], HdlcMode.ASYNC)
        expected = flag + self.ppp_frame.bytes() + flag
        self.assertEqual(expected, encoded)

