# from unittest import TestCase
#
# from bitstring import BitArray
#
# from layer2.hdlc.control_field import InformationCf, ExtendedSupervisoryCf, SupervisoryType
# from layer2.hdlc.hdlc import HdlcIFrame, HdlcFrameBase, HdlcExtendedSFrame, HdlcMode
# import layer1.manchester_encoding as me
#
#
# class Test(TestCase):
#     icf = InformationCf(pf=True, ns=17, nr=35)
#     information = b'Some information that we send in this frame!'
#     iframe = HdlcIFrame(address=129, control=icf, information=information)
#
#     # def test_encode(self):
#     #     flag = HdlcFrameBase.flag
#     #     encoded = encode([self.iframe, self.iframe], HdlcMode.NORMAL)
#     #     expected = BitArray(auto=flag + self.iframe.bytes() + flag + self.iframe.bytes() + flag)
#     #     self.assertEqual(expected, encoded)
#     #
#     # def test_encode_async(self):
#     #     flag = HdlcFrameBase.flag
#     #     encoded = encode([self.iframe, self.iframe], HdlcMode.ASYNC)
#     #     expected = BitArray(auto=flag + self.iframe.bytes() + flag + self.iframe.bytes() + flag)
#     #     self.assertEqual(expected, encoded)
#     #
#     # def test_encode_async_with_escaped_info(self):
#     #     information = b'Some information that' + HdlcFrameBase.flag + b' we send in this frame!'
#     #     escaped_information = b'Some information that' + HdlcFrameBase.escape_byte + HdlcFrameBase.flag \
#     #                           + b' we send in this frame!'
#     #     iframe = HdlcIFrame(address=129, control=self.icf, information=information)
#     #     flag = HdlcFrameBase.flag
#     #     encoded = encode([iframe, iframe], HdlcMode.ASYNC)
#     #     iframe_bytes = iframe.address.to_bytes(1, 'big') + iframe.control.bytes + escaped_information + iframe.fcs
#     #     expected = BitArray(auto=flag + iframe_bytes + flag + iframe_bytes + flag)
#     #     self.assertEqual(expected, encoded)
#
#     # def test_control_field_from(self):
#     #     ns_bits = "001"  # bits of 17 % 8
#     #     nr_bits = "011"  # bits of 35 % 8
#     #     bits = BitArray(bin="0" + ns_bits + "1" + nr_bits)
#     #     cf = control_field_from(bits.bytes)
#     #
#     #     expected = InformationCf(pf=True, ns=17, nr=35)
#     #     self.assertEqual(expected, cf)
#
#     # def test_single_hdlc_frame_from_physical(self):
#     #     phys_bits = encode([self.iframe], HdlcMode.NORMAL)
#     #     signal = me.encode(phys_bits)
#     #
#     #     frame,_ = decode_hdlc_frame_from(signal, HdlcMode.NORMAL)
#     #     self.assertEqual(self.iframe, frame)
#
#     # def test_single_hdlc_frame_from_physical_async(self):
#     #     phys_bits = encode([self.iframe], HdlcMode.ASYNC_BALANCED)
#     #     signal = me.encode(phys_bits)
#     #
#     #     frame = decode_hdlc_frame_from(signal, HdlcMode.ASYNC_BALANCED)
#     #     self.assertEqual(self.iframe, frame)
#     #
#     # def test_multiple_hdlc_frames_from_physical(self):
#     #     escf = ExtendedSupervisoryCf(pf=False, s_type=SupervisoryType.RR, nr=7)
#     #     esframe = HdlcExtendedSFrame(13, escf)
#     #     eicf = InformationCf(pf=True, ns=17, nr=35)
#     #     information = b'Some stuff that we transmit'
#     #     efframe = HdlcIFrame(address=129, control=eicf, information=information)
#     #
#     #     frames = [esframe, efframe, esframe, esframe, efframe]
#     #     phys_bits = encode(frames, HdlcMode.NORMAL)
#     #     signal = me.encode(phys_bits)
#     #
#     #     decoded = decode_signal_hdlc(signal, HdlcMode.NORMAL, extended=True)
#     #     self.assertEqual(frames, decoded)
#
#
#
#         # self.fail("Not implemented yet")
