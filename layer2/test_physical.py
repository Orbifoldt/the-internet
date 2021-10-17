from unittest import TestCase

from layer2.ethernet.ethernet import EthernetFrame
from layer2.hdlc.control_field import UnnumberedCf, ExtendedSupervisoryCf, SupervisoryType, UnnumberedType
from layer2.hdlc.hdlc import HdlcUFrame, HdlcExtendedSFrame
from layer2.hdlc_base import HdlcMode
from layer2.mac import Mac
from layer2.physical import create_ethernet_signal, create_hdlc_signal, decode_frames_hdlc, decode_frames_ethernet, \
    decode_frames_ppp
from layer2.ppp.point_to_point import PppProtocol, PppFrame


class TestPhysical(TestCase):
    payload1 = b'This is some ASCII encoded text that we put into this ethernet frame'
    payload2 = b'Received {}[]~! your #$(*@) message :)'
    dest = Mac.fromstring("a1:b2:c3:d4:e5:f6")
    src = Mac.fromstring("ff:11:aa:55:cc:99")

    def test_encode_then_decode_ethernet_frames(self):
        frame1 = EthernetFrame(self.dest, self.src, self.payload1)
        frame2 = EthernetFrame(self.src, self.dest, self.payload2)

        signal = create_ethernet_signal([frame1, frame2])
        decoded_frames = decode_frames_ethernet(signal)

        self.assertEqual(2, len(decoded_frames))
        self.assertEqual(frame1, decoded_frames[0])
        self.assertEqual(frame2, decoded_frames[1])

    ucf = UnnumberedCf(pf=False, u_type=UnnumberedType.SNRME)
    uframe = HdlcUFrame(13, ucf, payload1)
    ext_scf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.RR, nr=7)
    ext_sframe = HdlcExtendedSFrame(13, ext_scf)

    def test_encode_then_decode_hdlc_frames_extended_frames(self):
        signal = create_hdlc_signal([self.uframe, self.ext_sframe], HdlcMode.NORMAL)
        decoded_frames = decode_frames_hdlc(signal, mode=HdlcMode.NORMAL, extended=True)

        self.assertEqual(2, len(decoded_frames))
        self.assertEqual(self.uframe, decoded_frames[0])
        self.assertEqual(self.ext_sframe, decoded_frames[1])

    def test_encode_then_decode_hdlc_frames_extended_frames_async(self):
        signal = create_hdlc_signal([self.uframe, self.ext_sframe], HdlcMode.ASYNC_BALANCED)
        decoded_frames = decode_frames_hdlc(signal, mode=HdlcMode.ASYNC_BALANCED, extended=True)

        self.assertEqual(2, len(decoded_frames))
        self.assertEqual(self.uframe, decoded_frames[0])
        self.assertEqual(self.ext_sframe, decoded_frames[1])

    ppp_frame1 = PppFrame(PppProtocol.IPv4, payload2)
    ppp_frame2 = PppFrame(PppProtocol.IPv4, payload1)

    def test_encode_then_decode_ppp_frames(self):
        signal = create_hdlc_signal([self.ppp_frame1, self.ppp_frame2], HdlcMode.NORMAL)
        decoded_frames = decode_frames_ppp(signal, mode=HdlcMode.NORMAL)

        self.assertEqual(2, len(decoded_frames))
        self.assertEqual(self.ppp_frame1, decoded_frames[0])
        self.assertEqual(self.ppp_frame2, decoded_frames[1])
