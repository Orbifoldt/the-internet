from unittest import TestCase

from layer2.frame import encode, decode
from layer2.hdlc.control_field import InformationCf, ExtendedSupervisoryCf, SupervisoryType, ExtendedInfoCf, \
    UnnumberedType, UnnumberedCf
from layer2.hdlc.hdlc import HdlcIFrame, HdlcExtendedSFrame, HdlcExtendedIFrame, HdlcUFrame, HdlcFrame
from layer2.hdlc_base import HdlcMode


class TestDecoding(TestCase):
    icf = InformationCf(pf=True, ns=17, nr=35)
    information = b'Some information~that {we} [send] in this frame!'
    iframe = HdlcIFrame(address=129, control=icf, information=information)

    ext_scf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.RR, nr=7)
    ext_sframe = HdlcExtendedSFrame(13, ext_scf)

    ucf = UnnumberedCf(pf=False, u_type=UnnumberedType.SNRME)
    uframe = HdlcUFrame(13, ucf, information)


    def test_single_hdlc_frame_from_bits(self):
        bits = encode([self.iframe], HdlcMode.NORMAL)
        decoded_frames = decode(bits, HdlcFrame, mode=HdlcMode.NORMAL, extended=False)
        self.assertEqual([self.iframe], decoded_frames)

    def test_single_hdlc_frame_from_bits_async_mode(self):
        bits = encode([self.iframe], HdlcMode.ASYNC_BALANCED)
        decoded_frames = decode(bits, HdlcFrame, mode=HdlcMode.ASYNC_BALANCED, extended=False)
        self.assertEqual([self.iframe], decoded_frames)

    def test_single_extended_hdlc_frame_from_bits(self):
        bits = encode([self.ext_sframe], HdlcMode.NORMAL)
        decoded_frames = decode(bits, HdlcFrame, mode=HdlcMode.NORMAL, extended=True)
        self.assertEqual([self.ext_sframe], decoded_frames)

    def test_single_extended_hdlc_frame_from_bits_async_mode(self):
        bits = encode([self.ext_sframe], HdlcMode.ASYNC_BALANCED)
        decoded_frames = decode(bits, HdlcFrame, mode=HdlcMode.ASYNC_BALANCED, extended=True)
        self.assertEqual([self.ext_sframe], decoded_frames)

    def test_multiple_extended_hdlc_frames_from_bits(self):
        eicf = ExtendedInfoCf(pf=True, ns=17, nr=35)
        information = b'Some stuff that we transmit'
        ext_fframe = HdlcExtendedIFrame(address=129, control=eicf, information=information)

        frames = [self.uframe, self.ext_sframe, ext_fframe, self.ext_sframe, self.ext_sframe, ext_fframe]
        bits = encode(frames, HdlcMode.NORMAL)

        decoded_frames = decode(bits, HdlcFrame, mode=HdlcMode.NORMAL, extended=True)
        self.assertEqual(frames, decoded_frames)

    def test_multiple_extended_hdlc_frames_from_bits_async_mode(self):
        eicf = ExtendedInfoCf(pf=True, ns=17, nr=35)
        information = b'Some stuff that we transmit'
        ext_fframe = HdlcExtendedIFrame(address=129, control=eicf, information=information)

        frames = [self.uframe, self.ext_sframe, ext_fframe, self.ext_sframe, self.ext_sframe, ext_fframe]
        bits = encode(frames, HdlcMode.ASYNC_BALANCED)

        decoded_frames = decode(bits, HdlcFrame, mode=HdlcMode.ASYNC_BALANCED, extended=True)
        self.assertEqual(frames, decoded_frames)

