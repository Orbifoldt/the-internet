from unittest import TestCase

from bitstring import BitArray

from layer2.hdlc.control_field import InformationCf, ExtendedSupervisoryCf, SupervisoryType, ExtendedInfoCf, \
    UnnumberedCf, UnnumberedType
from layer2.hdlc.decoding import interpret_control_field_from, decode
from layer2.frame import encode
from layer2.hdlc.hdlc import HdlcIFrame, HdlcExtendedSFrame, HdlcExtendedIFrame, HdlcUFrame
from layer2.hdlc_base import HdlcMode
from layer2.tools import bits_to_bytes


class Test(TestCase):
    icf = InformationCf(pf=True, ns=17, nr=35)
    information = b'Some information~that {we} [send] in this frame!'
    iframe = HdlcIFrame(address=129, control=icf, information=information)

    ext_scf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.RR, nr=7)
    ext_sframe = HdlcExtendedSFrame(13, ext_scf)

    ucf = UnnumberedCf(pf=False, u_type=UnnumberedType.SNRME)
    uframe = HdlcUFrame(13, ucf, information)

    def test_info_control_field_from(self):
        ns_bits = "001"  # bits of 17 % 8
        nr_bits = "011"  # bits of 35 % 8
        bits = BitArray(bin="0" + ns_bits + "1" + nr_bits)
        cf = interpret_control_field_from(bits.bytes)

        expected = InformationCf(pf=True, ns=17, nr=35)
        self.assertEqual(expected, cf)

    def test_extended_info_control_field_from(self):
        ns_bits = "0010001"  # bits of 17
        nr_bits = "0100011"  # bits of 35
        bits = BitArray(bin="0" + ns_bits + "1" + nr_bits)
        cf = interpret_control_field_from(bits.bytes)

        expected = ExtendedInfoCf(pf=True, ns=17, nr=35)
        self.assertEqual(expected, cf)

    def test_unnumbered_control_field_from(self):
        bits = self.ucf.bits
        cf = interpret_control_field_from(bits_to_bytes(list(bits)))
        self.assertEqual(self.ucf, cf)

