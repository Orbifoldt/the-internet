from __future__ import annotations

from abc import abstractmethod

from bitstring import BitArray

from layer2.hdlc.control_field import ControlField, InformationCf, SupervisoryCf, UnnumberedCf, ExtendedInfoCf, \
    ExtendedSupervisoryCf, SupervisoryType, UnnumberedType
from layer2.hdlc_base import HdlcLikeBaseFrame
from layer2.tools import crc32, bits_to_int


class HdlcFrame(HdlcLikeBaseFrame):
    @abstractmethod
    def __init__(self, address: int, control: ControlField, information: bytes = None) -> None:
        super().__init__(address, control, information, optional_field=None)

    @classmethod
    def interpret_frame_from_bytes(cls, decoded_bytes: bytes, **kwargs):
        return HdlcFrame.decode_frame_from_bytes(decoded_bytes, kwargs['extended'])

    @staticmethod
    def decode_frame_from_bytes(frame_bytes: bytes, extended: bool) -> HdlcFrame:
        """
        Decode a single HDLC frame from the provided frame_bytes, or raise an ValueError if bytes are not compatible.
        """
        if (n := len(frame_bytes)) < 6:
            raise ValueError(f"Received frame of length {n} which can't be processed as HDLC.", n)

        end_control_index = 3 if (not HdlcFrame.is_u_frame(frame_bytes[1:2]) and extended) else 2
        address = frame_bytes[0]
        control_bytes = frame_bytes[1:end_control_index]
        information = frame_bytes[end_control_index:-4]
        fcs = frame_bytes[-4:]

        calculated_fcs = crc32(frame_bytes[:-4])
        if fcs != calculated_fcs:
            raise ValueError(f"The calculated FCS '{calculated_fcs}' does not equal FCS of the received frame: '{fcs}'",
                             n, address, control_bytes, frame_bytes)

        control_field = HdlcFrame.interpret_control_field_from(control_bytes)
        return HdlcFrame.construct_hdlc_frame(address, control_field, information)

    @staticmethod
    def is_u_frame(control_bytes: bytes) -> bool:
        bits = BitArray(auto=control_bytes)
        return bits[0] == 1 and bits[1] == 1

    @staticmethod
    def is_i_frame(control_bytes: bytes) -> bool:
        bits = BitArray(auto=control_bytes)
        return bits[0] == 0

    @staticmethod
    def interpret_control_field_from(control_bytes: bytes):
        """
        By interpreting the bits of the control_bytes this returns a ControlField sub-type
        """
        extended = len(control_bytes) == 2
        bits = BitArray(auto=control_bytes)

        pf_index = 8 if extended else 4
        part1_index = 1 if HdlcFrame.is_i_frame(control_bytes) else 2
        pf = bits[pf_index]
        x1 = bits_to_int(bits[part1_index:pf_index])
        x2 = bits_to_int(bits[pf_index + 1:])

        if not bits[0]:  # I-Frame = 0...
            if extended:
                return ExtendedInfoCf(pf, ns=x1, nr=x2)
            else:
                return InformationCf(pf, ns=x1, nr=x2)
        else:
            if not bits[1]:  # S-Frame = 10...
                s_type = SupervisoryType(x1)
                if extended:
                    return ExtendedSupervisoryCf(pf, s_type, nr=x2)
                else:
                    return SupervisoryCf(pf, s_type, nr=x2)
            else:  # U-Frame = 11...
                u_type = UnnumberedType((x1, x2))
                return UnnumberedCf(pf, u_type)

    @staticmethod
    def construct_hdlc_frame(address: int, control: ControlField, information: bytes) -> HdlcFrame:
        """
        By looking at the type of the control this creates a specific HDLC frame with specified arguments.
        """
        match control:
            case ExtendedInfoCf():
                return HdlcExtendedIFrame(address, control, information)
            case InformationCf():
                return HdlcIFrame(address, control, information)
            case ExtendedSupervisoryCf():
                return HdlcExtendedSFrame(address, control)
            case SupervisoryCf():
                return HdlcSFrame(address, control)
            case UnnumberedCf():
                return HdlcUFrame(address, control, information)
        raise ValueError("The control field is not recognized.")


class HdlcIFrame(HdlcFrame):
    def __init__(self, address: int, control: InformationCf, information: bytes) -> None:
        if isinstance(control, ExtendedInfoCf):
            raise TypeError("Extended control frames not supported, please use HdlcExtendedIFrame")
        super().__init__(address, control, information)


class HdlcExtendedIFrame(HdlcFrame):
    def __init__(self, address: int, control: ExtendedInfoCf, information: bytes) -> None:
        super().__init__(address, control, information)


class HdlcSFrame(HdlcFrame):
    def __init__(self, address: int, control: SupervisoryCf) -> None:
        if isinstance(control, ExtendedSupervisoryCf):
            raise TypeError("Extended control frames not supported, please use HdlcExtendedSFrame")
        super().__init__(address, control)


class HdlcExtendedSFrame(HdlcFrame):
    def __init__(self, address: int, control: ExtendedSupervisoryCf) -> None:
        super().__init__(address, control)


class HdlcUFrame(HdlcFrame):
    def __init__(self, address: int, control: UnnumberedCf, information: bytes) -> None:
        super().__init__(address, control, information)
