from unittest import TestCase

from bitstring import BitArray

from layer2.hdlc.control_field import InformationCf
from layer2.frame import encode, encode_bytes
from layer2.hdlc.hdlc import HdlcIFrame, HdlcFrame
from layer2.hdlc_base import HdlcMode


class Test(TestCase):
    icf = InformationCf(pf=True, ns=17, nr=35)
    information = b'Some information that we send in this frame!'
    iframe = HdlcIFrame(address=129, control=icf, information=information)

    def test_encode(self):
        flag = HdlcFrame.flag
        encoded = encode([self.iframe], HdlcMode.NORMAL)
        expected = BitArray(auto=flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_multiple_frames(self):
        flag = HdlcFrame.flag
        encoded = encode([self.iframe, self.iframe], HdlcMode.NORMAL)
        expected = BitArray(auto=flag + self.iframe.bytes() + flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_async_mode(self):
        flag = HdlcFrame.flag
        encoded = encode([self.iframe], HdlcMode.ASYNC)
        expected = BitArray(auto=flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_async_balanced_mode(self):
        flag = HdlcFrame.flag
        encoded = encode([self.iframe], HdlcMode.ASYNC_BALANCED)
        expected = BitArray(auto=flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_async_mode_multiple_frames(self):
        flag = HdlcFrame.flag
        encoded = encode([self.iframe, self.iframe], HdlcMode.ASYNC)
        expected = BitArray(auto=flag + self.iframe.bytes() + flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_async_mode_with_escaped_info(self):
        information = b'Some information that' + HdlcFrame.flag + b' we send' + HdlcFrame.escape_byte + \
                      b' in this frame!'
        escaped_information = b'Some information that' + HdlcFrame.escape_byte + b'\x5E' \
                              + b' we send' + HdlcFrame.escape_byte + b'\x5D' + b' in this frame!'
        iframe = HdlcIFrame(address=129, control=self.icf, information=information)
        flag = HdlcFrame.flag
        encoded = encode([iframe, iframe], HdlcMode.ASYNC)
        iframe_bytes = iframe.address.to_bytes(1, 'big') + iframe.control.bytes + escaped_information + iframe.fcs
        expected = BitArray(auto=flag + iframe_bytes + flag + iframe_bytes + flag)
        self.assertEqual(expected, encoded)

    def test_encode_bytes_async_mode(self):
        flag = HdlcFrame.flag
        encoded = encode([self.iframe], HdlcMode.ASYNC)
        expected = BitArray(auto=flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_encode_bytes_normal_mode_raises_value_error(self):
        with self.assertRaises(ValueError):
            encode_bytes([self.iframe], HdlcMode.NORMAL)
