# from typing import Callable
#
# from bitstring import BitArray
#
# from layer2.hdlc.control_field import ExtendedInfoCf, InformationCf, SupervisoryType, ExtendedSupervisoryCf, \
#     SupervisoryCf, UnnumberedCf, UnnumberedType
# from layer2.hdlc.hdlc import HdlcFrameBase, HdlcMode, construct_frame
# from layer2.receive_data_physical import decode_frame_bits, decode_frame_bytes
# from layer2.tools import bits_to_bytes, crc32, bits_to_int
# from layer2.receive_data import stuff_bits, destuff_bits, escape_bytes, encode_bits_with_flag, encode_with_flag
#

# def decode_hdlc_frame_from(signal: Callable[[float], float], mode: HdlcMode, extended: bool = False) -> tuple[
#     HdlcFrameBase, int]:
#     flag = HdlcFrameBase.flag
#     if mode == HdlcMode.NORMAL:
#         frame_bits = decode_frame_bits(signal, start_flag=BitArray(auto=flag), end_flag=BitArray(auto=flag))
#         destuffed = destuff_bits(list(frame_bits), HdlcFrameBase.bits_to_stuff + [HdlcFrameBase.stuffing_bit])
#         if len(destuffed) % 8 != 0:
#             raise ValueError(f"Frame decoded from signal contained {len(destuffed)} bits, expected multiple of 8")
#         frame_bytes = bits_to_bytes(destuffed)
#     else:
#         frame_bytes = decode_frame_bytes(signal, start_flag=flag, end_flag=flag, escape=HdlcFrameBase.escape_byte)
#
#     if (n := len(frame_bytes)) < 6:
#         raise ValueError(f"Received frame of length {n} which can't be processed.", n)
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
#     control_field = control_field_from(control_bytes)
#     return construct_frame(address, control_field, information), n
#
#
# def decode_signal_hdlc(signal: Callable[[float], float], mode: HdlcMode, extended: bool = False) -> list[HdlcFrameBase]:
#     offset = 0
#     frames = []
#     count = 0
#     n=0
#     while True:
#         offset_signal = lambda t: signal(t + n)
#         try:
#             frame, n = decode_hdlc_frame_from(offset_signal, mode, extended)
#             frames.append(frame)
#             offset += n*8-8
#             count +=1
#             if count > 100:
#                 break
#         except:
#             print("broke")
#             break
#     return frames
#
#
# def control_field_from(control_bytes: bytes):
#     extended = len(control_bytes) == 2
#     bits = BitArray(auto=control_bytes)
#
#     pf_index = 8 if extended else 4
#     pf = bits[pf_index]
#     x1 = bits_to_int(bits[1:pf_index])
#     x2 = bits_to_int(bits[pf_index + 1:])
#
#     if not bits[0]:  # I-Frame
#         if extended:
#             return ExtendedInfoCf(pf, ns=x1, nr=x2)
#         else:
#             return InformationCf(pf, ns=x1, nr=x2)
#     else:
#         if not bits[1]:  # S-Frame
#             s_type = SupervisoryType(x1)
#             if extended:
#                 return ExtendedSupervisoryCf(pf, s_type, nr=x2)
#             else:
#                 return SupervisoryCf(pf, s_type, nr=x2)
#         else:  # U-Frame
#             u_type = UnnumberedType((x1, x2))
#             return UnnumberedCf(pf, u_type)
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
# def encode(frames: list[HdlcFrameBase], mode: HdlcMode) -> BitArray:
#     if mode == HdlcMode.NORMAL:
#         stuffed_bits = [BitArray(auto=stuff_bits(f.bits(), HdlcFrameBase.bits_to_stuff, HdlcFrameBase.stuffing_bit)) for f in frames]
#         # stuffed_bytes = [BitArray(bin="".join(["1" if b else "0" for b in x])).bytes for x in stuffed_bits]
#         # stuffed_bytes = [x.bytes for x in stuffed_bits]
#         encoded_bytes = encode_bits_with_flag(stuffed_bits, HdlcFrameBase.flag)
#         return BitArray(auto=encoded_bytes)
#     else:
#         stuffed_bytes = [escape_bytes(x.bytes(), HdlcFrameBase.flag, HdlcFrameBase.escape_byte) for x in frames]
#
#     encoded_bytes = encode_with_flag(stuffed_bytes, HdlcFrameBase.flag)
#     return BitArray(auto=encoded_bytes)
