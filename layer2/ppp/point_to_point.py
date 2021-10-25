from enum import Enum
from typing import Final

from bitstring import BitArray

from layer2.hdlc.control_field import ControlField
from layer2.hdlc_base import HdlcLikeBaseFrame
from layer2.tools import crc32


class PppControlField(ControlField):
    def __init__(self):
        super().__init__(BitArray(auto=b'\x03'), False)


class PppProtocol(Enum):
    # Network Layer Protocols 0xxx-3xxx
    IPv4 = 0x0021
    IPv6 = 0x0057
    APPLE_TALK = 0x0029
    IPX = 0x002B
    MULTILINK = 0x003D
    NET_BIOS = 0x003F

    # Network Control Protocols 8xxx-Bxxx
    IPCP = 0x8021
    IPv6CP = 0x8057

    # Link-layer Control Protocols Cxxx-Fxxx
    LCP = 0xC021


class PppFrame(HdlcLikeBaseFrame):
    default_address: Final = 0xFF

    def __init__(self, protocol: PppProtocol, information: bytes = None):
        self.protocol = protocol
        self.protocol_bytes = self.protocol.value.to_bytes(2, 'big')
        super().__init__(self.default_address, PppControlField(), information, optional_field=self.protocol_bytes)

    @classmethod
    def interpret_frame_from_bytes(cls, decoded_bytes: bytes, **kwargs):
        return PppFrame.decode_ppp_frame_from_bytes(decoded_bytes)

    @staticmethod
    def decode_ppp_frame_from_bytes(decoded_bytes: bytes):
        """
        Decode a single HDLC frame from the provided frame_bytes, or raise an ValueError if bytes are not compatible.
        """
        if (n := len(decoded_bytes)) < 8:
            raise ValueError(f"Received frame of length {n} which can't be processed as PPP.", n)

        address = decoded_bytes[0]
        control_bytes = decoded_bytes[1:2]
        protocol_bytes = decoded_bytes[2:4]
        information = decoded_bytes[4:-4]
        fcs = decoded_bytes[-4:]

        calculated_fcs = crc32(decoded_bytes[:-4])
        if fcs != calculated_fcs:
            raise ValueError(f"The calculated FCS '{calculated_fcs}' does not equal FCS of the received frame: '{fcs}'",
                             n, address, control_bytes, decoded_bytes)
        if address != PppFrame.default_address:
            raise ValueError(f"Invalid address received for a PPP frame: {address}.")
        if control_bytes != PppControlField().bytes:
            raise ValueError(f"Invalid control field received for a PPP frame: {control_bytes}.")

        protocol = PppProtocol(int.from_bytes(protocol_bytes, byteorder='big'))
        return PppFrame(protocol, information)
