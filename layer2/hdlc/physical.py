from typing import Callable

from bitstring import BitArray

import layer1.manchester_encoding as me
from layer2.hdlc.control_field import ExtendedInfoCf, InformationCf, SupervisoryType, ExtendedSupervisoryCf, \
    SupervisoryCf, UnnumberedCf, UnnumberedType
from layer2.hdlc.hdlc import HdlcFrameBase, HdlcMode
from layer2.receive_data import decode_frame_bits, decode_frame_bytes
from layer2.tools import destuff_bits, bits_to_bytes, crc32, bits_to_int


def hdlc_frame_from(signal: Callable[[float], float], mode: HdlcMode, extended: bool = False) -> HdlcFrameBase:
    flag = HdlcFrameBase.flag
    if mode == HdlcMode.NORMAL:
        frame_bits = decode_frame_bits(signal, start_flag=BitArray(auto=flag), end_flag=BitArray(auto=flag))
        destuffed = destuff_bits(list(frame_bits), HdlcFrameBase.bits_to_stuff + [HdlcFrameBase.stuffing_bit])
        if len(destuffed) % 8 != 0:
            raise ValueError(f"Frame decoded from signal contained {len(destuffed)} bits, expected multiple of 8")
        frame_bytes = bits_to_bytes(destuffed)
    else:
        frame_bytes = decode_frame_bytes(signal, start_flag=flag, end_flag=flag, escape=HdlcFrameBase.escape_byte)

    end_control_index = 3 if (not is_u_frame(frame_bytes[1:2]) and extended) else 2
    address = frame_bytes[0]
    control_bytes = frame_bytes[1:end_control_index]
    information = frame_bytes[end_control_index:-4]
    fcs = frame_bytes[-4:]

    calculated_fcs = crc32(frame_bytes[:-4])
    if fcs != calculated_fcs:
        raise ValueError(f"The calculated FCS '{calculated_fcs}' does not equal FCS of the received frame: '{fcs}'",
                         address, control_bytes, frame_bytes)

    control_field = control_field_from(control_bytes)

    # then return the frame object



def control_field_from(control_bytes: bytes):
    extended = len(control_bytes) == 2
    bits = BitArray(auto=control_bytes)

    pf_index = 8 if extended else 4
    pf = bits[pf_index]
    x1 = bits_to_int(bits[1:pf_index])
    x2 = bits_to_int(bits[pf_index + 1:])

    if not bits[0]:  # I-Frame
        if extended:
            return ExtendedInfoCf(pf, ns=x1, nr=x2)
        else:
            return InformationCf(pf, ns=x1, nr=x2)
    else:
        if not bits[1]:  # S-Frame
            s_type = SupervisoryType(x1)
            if extended:
                return ExtendedSupervisoryCf(pf, s_type, nr=x2)
            else:
                return SupervisoryCf(pf, s_type, nr=x2)
        else:  # U-Frame
            u_type = UnnumberedType((x1, x2))
            return UnnumberedCf(pf, u_type)


def is_u_frame(control_bytes: bytes) -> bool:
    bits = BitArray(auto=control_bytes)
    return bits[0] == 1 and bits[1] == 1

def is_i_frame(control_bytes: bytes) -> bool:
    bits = BitArray(auto=control_bytes)
    return bits[0] == 0
