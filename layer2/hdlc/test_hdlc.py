from unittest import TestCase

from layer2.hdlc.control_field import SupervisoryType, UnnumberedType
from layer2.hdlc.hdlc import *


class TestHdlcFrame(TestCase):

    def test_hdlc_base_frame_cant_be_instantiated(self):
        with self.assertRaises(TypeError):
            HdlcFrameBase(5, SupervisoryCf(True, SupervisoryType.REJ, 7))

    def test_hdlc_info_frame(self):
        icf = InformationCf(pf=True, ns=17, nr=35)
        information = b'Some information that we send in this frame!'
        iframe = HdlcIFrame(address=129, control=icf, information=information)

        header = BitArray(bin="10000001" + "00011011").bytes
        expected = header + information + 0x74C562DA.to_bytes(4, byteorder='big')
        self.assertEqual(expected, iframe.bytes())

    def test_extended_hdlc_info_frame(self):
        eicf = ExtendedInfoCf(pf=True, ns=17, nr=37)
        information = b'Some information that we send in this frame!'
        ext_iframe = HdlcExtendedIFrame(address=129, control=eicf, information=information)

        header = BitArray(bin="10000001" + "0001000110100101").bytes
        expected = header + information + 0x1AC2467B.to_bytes(4, byteorder='big')
        self.assertEqual(expected, ext_iframe.bytes())

    def test_extended_info_frame_with_non_extended_cf_should_raise_error(self):
        information = b'Some information that we send in this frame!'
        extended_icf = ExtendedInfoCf(pf=True, ns=17, nr=37)
        with self.assertRaises(TypeError):
            HdlcIFrame(address=129, control=extended_icf, information=information)

    def test_hdlc_supervisory_frame(self):
        scf = SupervisoryCf(pf=True, s_type=SupervisoryType.RNR, nr=3)
        sframe = HdlcSFrame(address=78, control=scf)

        expected = BitArray(bin="01001110" + "10101011").bytes + 0x140A276E.to_bytes(4, byteorder='big')
        self.assertEqual(expected, sframe.bytes())

    def test_extended_hdlc_supervisory_frame(self):
        eicf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.SREJ, nr=37)
        ext_sframe = HdlcExtendedSFrame(address=129, control=eicf)

        expected = BitArray(bin="10000001" + "1000001100100101").bytes + 0x6AB71C44.to_bytes(4, byteorder='big')
        self.assertEqual(expected, ext_sframe.bytes())

    def test_extended_supervisory_frame_with_non_extended_cf_should_raise_error(self):
        extended_icf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.SREJ, nr=99)
        with self.assertRaises(TypeError):
            HdlcSFrame(address=129, control=extended_icf)

    def test_hdlc_unnumbered_frame(self):
        information = b'We can give information in here@@@@###'
        ucf = UnnumberedCf(pf=False, u_type=UnnumberedType.DISC)
        uframe = HdlcUFrame(address=78, control=ucf, information=information)

        header = BitArray(bin="01001110" + "11000010").bytes
        expected = header + information + 0x7BB082AD.to_bytes(4, byteorder='big')
        self.assertEqual(expected, uframe.bytes())
