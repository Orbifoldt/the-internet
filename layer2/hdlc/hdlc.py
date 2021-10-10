from abc import ABC, abstractmethod
from enum import Enum

from bitstring import BitArray

from layer2.hdlc.control_field import ControlField, InformationCf, SupervisoryCf, UnnumberedCf, ExtendedInfoCf, \
    ExtendedSupervisoryCf
from layer2.tools import crc32


class HdlcMode(Enum):
    NORMAL = 0
    ASYNC = 1
    ASYNC_BALANCED = 2


class HdlcFrameBase(ABC):
    flag = int("01111110", 2).to_bytes(1, byteorder='big')
    escape_byte = int("10111110", 2).to_bytes(1, byteorder='big')
    bits_to_stuff = [c == '1' for c in "11111"]
    stuffing_bit = False

    @abstractmethod
    def __init__(self, address: int, control: ControlField, information: bytes = None) -> None:
        if not (0 <= address < 2 ** 8):
            raise ValueError("Address must not be >= 0 and < 256")
        self.address = address
        self.control = control
        if information is None:
            self.information = bytes()
        else:
            self.information = information
        self.fcs = self.calculate_fcs()

    def bytes(self):
        return self.address.to_bytes(1, 'big') + self.control.bytes + self.information + self.fcs

    def bits(self):
        return BitArray(auto=self.bytes())

    def calculate_fcs(self):
        all_data = self.address.to_bytes(1, 'big') + self.control.bytes + self.information
        return crc32(all_data)


class HdlcIFrame(HdlcFrameBase):
    def __init__(self, address: int, control: InformationCf, information: bytes) -> None:
        if isinstance(control, ExtendedInfoCf):
            raise TypeError("Extended control frames not supported, please use HdlcExtendedIFrame")
        super().__init__(address, control, information)


class HdlcExtendedIFrame(HdlcFrameBase):
    def __init__(self, address: int, control: ExtendedInfoCf, information: bytes) -> None:
        super().__init__(address, control, information)


class HdlcSFrame(HdlcFrameBase):
    def __init__(self, address: int, control: SupervisoryCf) -> None:
        if isinstance(control, ExtendedSupervisoryCf):
            raise TypeError("Extended control frames not supported, please use HdlcExtendedSFrame")
        super().__init__(address, control)


class HdlcExtendedSFrame(HdlcFrameBase):
    def __init__(self, address: int, control: ExtendedSupervisoryCf) -> None:
        super().__init__(address, control)


class HdlcUFrame(HdlcFrameBase):
    def __init__(self, address: int, control: UnnumberedCf, information: bytes) -> None:
        super().__init__(address, control, information)


# def constructor(address: int, control: ControlField, information: bytes):
#     match control:
#         case ExtendedInfoCf(_,_,_):
#             HdlcExtendedIFrame(address, control, information)

