# from bitstring import BitArray
#
# from layer2.hdlc.control_field import ExtendedInfoCf, InformationCf, SupervisoryType, ExtendedSupervisoryCf, \
#     SupervisoryCf, UnnumberedCf, UnnumberedType, ControlField
# from layer2.hdlc.hdlc import HdlcFrame, HdlcExtendedIFrame, HdlcIFrame, HdlcExtendedSFrame, HdlcSFrame, \
#     HdlcUFrame
# from layer2.hdlc_base import HdlcMode
# from layer2.tools import separate, bits_to_bytes, bits_to_int, crc32, destuff_bits
#
#
# def decode(data: BitArray, mode: HdlcMode, extended: bool = False) -> list[HdlcFrame]:
#     """
#     Decode HDLC frames from a source "bit-stream" (a BitArray) using the specified HDLC mode.
#     :param data: The data source for the bits
#     :param mode: HdlcMode that is used for the associated connection (determines if bit or byte stuffing was used)
#     :param extended: if extended frames are being used or not
#     :return: All valid HDLC frames. Invalid ones are silently dropped.
#     """
#     bit_sections = separate(list(data), list(HdlcFrame.flag_bits))
#     if mode == HdlcMode.NORMAL:
#         frames_bytes = [destuff_section(section) for section in bit_sections]
#     else:
#         frames_bytes = [HdlcFrame.escape_schema.unescape(bits_to_bytes(section)) for section in bit_sections]
#     return safe_decode_frames(frames_bytes, extended)
#
#
# def decode_bytes(data: bytes, mode: HdlcMode, extended: bool = False) -> list[HdlcFrame]:
#     """
#     Decode HDLC frames from a byte source using a specified HDLC mode.
#     """
#     if mode == HdlcMode.NORMAL:
#         raise ValueError("Byte-encoding not supported for NORMAL mode: bit stuffing not compatible with byte format")
#     else:
#         return decode(BitArray(auto=data), mode, extended)
#
#
# def destuff_section(section: list[bool]) -> bytes:
#     destuffed = destuff_bits(section, HdlcFrame.bits_to_stuff, HdlcFrame.stuffing_bit)
#     if len(destuffed) % 8 != 0:
#         raise ValueError(f"Decoded frame contained {len(destuffed)} bits, multiple of 8 needed to read as bytes")
#     return bits_to_bytes(destuffed)
#
#
# def safe_decode_frames(frames_bytes: list[bytes], extended: bool) -> list[HdlcFrame]:
#     """
#     Decode the HDLC frame for each element of frames_bytes, or drop it if an error occurs
#     """
#     received_frames = []
#     for byte_frame in frames_bytes:
#         try:
#             received_frames.append(decode_frame_from_bytes(byte_frame, extended))
#         except ValueError as e:
#             print(f"Error while receiving frame: {e}. It will be dropped.")
#     return received_frames
#
#
# def decode_frame_from_bytes(frame_bytes: bytes, extended: bool) -> HdlcFrame:
#     """
#     Decode a single HDLC frame from the provided frame_bytes, or raise an ValueError if bytes are not compatible.
#     """
#     if (n := len(frame_bytes)) < 6:
#         raise ValueError(f"Received frame of length {n} which can't be processed.", n)
#
#     end_control_index = 3 if (not is_u_frame(frame_bytes[1:2]) and extended) else 2
#     address = frame_bytes[0]
#     control_bytes = frame_bytes[1:end_control_index]
#     information = frame_bytes[end_control_index:-4]
#     fcs = frame_bytes[-4:]
#
#     calculated_fcs = crc32(frame_bytes[:-4])
#     if fcs != calculated_fcs:
#         raise ValueError(f"The calculated FCS '{calculated_fcs}' does not equal FCS of the received frame: '{fcs}'", n,
#                          address, control_bytes, frame_bytes)
#
#     control_field = interpret_control_field_from(control_bytes)
#     return construct_frame(address, control_field, information)
#
#
# def is_u_frame(control_bytes: bytes) -> bool:
#     bits = BitArray(auto=control_bytes)
#     return bits[0] == 1 and bits[1] == 1
#
#
# def is_i_frame(control_bytes: bytes) -> bool:
#     bits = BitArray(auto=control_bytes)
#     return bits[0] == 0
#
#
# def interpret_control_field_from(control_bytes: bytes):
#     """
#     By interpreting the bits of the control_bytes this returns a ControlField sub-type
#     """
#     extended = len(control_bytes) == 2
#     bits = BitArray(auto=control_bytes)
#
#     pf_index = 8 if extended else 4
#     part1_index = 1 if is_i_frame(control_bytes) else 2
#     pf = bits[pf_index]
#     x1 = bits_to_int(bits[part1_index:pf_index])
#     x2 = bits_to_int(bits[pf_index + 1:])
#
#     if not bits[0]:  # I-Frame = 0...
#         if extended:
#             return ExtendedInfoCf(pf, ns=x1, nr=x2)
#         else:
#             return InformationCf(pf, ns=x1, nr=x2)
#     else:
#         if not bits[1]:  # S-Frame = 10...
#             s_type = SupervisoryType(x1)
#             if extended:
#                 return ExtendedSupervisoryCf(pf, s_type, nr=x2)
#             else:
#                 return SupervisoryCf(pf, s_type, nr=x2)
#         else:  # U-Frame = 11...
#             u_type = UnnumberedType((x1, x2))
#             return UnnumberedCf(pf, u_type)
#
#
# def construct_frame(address: int, control: ControlField, information: bytes) -> HdlcFrame:
#     """
#     By looking at the type of the control this creates a specific HDLC frame with specified arguments.
#     """
#     match control:
#         case ExtendedInfoCf():
#             return HdlcExtendedIFrame(address, control, information)
#         case InformationCf():
#             return HdlcIFrame(address, control, information)
#         case ExtendedSupervisoryCf():
#             return HdlcExtendedSFrame(address, control)
#         case SupervisoryCf():
#             return HdlcSFrame(address, control)
#         case UnnumberedCf():
#             return HdlcUFrame(address, control, information)
#     raise ValueError("The control field is not recognized.")
