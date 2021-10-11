from unittest import TestCase

from layer2.hdlc.control_field import *


class TestControlField(TestCase):
    def test_ControlField_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            ControlField(BitArray(auto=[0, 1, 0, 1, 0, 1, 0, 1]), True)

    def test_equality_information_cf(self):
        icf1 = InformationCf(pf=True, ns=17, nr=35)
        icf2 = InformationCf(pf=True, ns=1, nr=3)
        self.assertTrue(icf1 == icf2)

    def test_inequality_information_cf(self):
        icf1 = InformationCf(pf=True, ns=5, nr=3)
        icf2 = InformationCf(pf=True, ns=1, nr=3)
        self.assertFalse(icf1 == icf2)

    def test_inequality_two_cf(self):
        icf = InformationCf(pf=True, ns=1, nr=3)
        scf = SupervisoryCf(pf=True, s_type=SupervisoryType.REJ, nr=3)
        self.assertFalse(icf == scf)

    def test_create_information_cf(self):
        icf = InformationCf(pf=True, ns=17, nr=35)
        ns_bits = "001"  # bits of 17 % 8
        nr_bits = "011"  # bits of 35 % 8
        self.assertEqual(BitArray(bin="0" + ns_bits + "1" + nr_bits), icf.bits)

    def test_create_extended_information_cf(self):
        eicf = ExtendedInfoCf(pf=False, ns=17, nr=37)
        ns_bits = "0010001"  # bits of 17 % 128
        nr_bits = "0100101"  # bits of 37 % 128
        self.assertEqual(BitArray(bin="0" + ns_bits + "0" + nr_bits), eicf.bits)

    def test_create_supervisory_cf(self):
        scf = SupervisoryCf(pf=False, s_type=SupervisoryType.REJ, nr=35)
        type_bits = "01"  # REJ=01
        nr_bits = "011"  # bits of 35 % 8
        self.assertEqual(BitArray(bin="10" + type_bits + "0" + nr_bits), scf.bits)

    def test_create_extended_supervisory_cf(self):
        escf = ExtendedSupervisoryCf(pf=True, s_type=SupervisoryType.RNR, nr=541)
        type_bits = "0000" + "10"  # padding + RNR=10
        nr_bits = "0011101"  # bits of 541 % 128
        self.assertEqual(BitArray(bin="10" + type_bits + "1" + nr_bits), escf.bits)

    def test_create_unnumbered_cf(self):
        ucf = UnnumberedCf(pf=True, u_type=UnnumberedType.RSET)
        m1_bits = "11"
        m2_bits = "001"
        self.assertEqual(BitArray(bin="11" + m1_bits + "1" + m2_bits), ucf.bits)
