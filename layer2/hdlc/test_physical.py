from unittest import TestCase

from bitstring import BitArray

from layer2.hdlc.control_field import InformationCf, ExtendedSupervisoryCf, SupervisoryType
from layer2.hdlc.hdlc import HdlcIFrame, HdlcFrameBase, HdlcExtendedSFrame, HdlcMode
from layer2.hdlc.physical import encode, control_field_from, hdlc_frame_from
import layer1.manchester_encoding as me


class Test(TestCase):
    icf = InformationCf(pf=True, ns=17, nr=35)
    information = b'Some information that we send in this frame!'
    iframe = HdlcIFrame(address=129, control=icf, information=information)

    def test_encode(self):
        flag = HdlcFrameBase.flag
        encoded = encode([self.iframe, self.iframe])
        expected = BitArray(auto=flag + self.iframe.bytes() + flag + self.iframe.bytes() + flag)
        self.assertEqual(expected, encoded)

    def test_control_field_from(self):
        ns_bits = "001"  # bits of 17 % 8
        nr_bits = "011"  # bits of 35 % 8
        bits = BitArray(bin="0" + ns_bits + "1" + nr_bits)
        cf = control_field_from(bits.bytes)

        expected = InformationCf(pf=True, ns=17, nr=35)
        self.assertEqual(expected, cf)

    def test_hdlc_frame_from(self):
        phys_bits = encode([self.iframe], HdlcMode.NORMAL)
        signal = me.encode(phys_bits)

        frame = hdlc_frame_from(signal, HdlcMode.NORMAL)
        self.assertEqual(self.iframe, frame)

    def test_hdlc_frame_from2(self):
        cf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.RR, nr=7)
        frame = HdlcExtendedSFrame(13, cf)

        self.fail("Not implemented yet")
