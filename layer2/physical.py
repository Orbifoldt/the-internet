from typing import Callable

from bitstring import BitArray

import layer2.ethernet.encoding as eenc
import layer2.ethernet.decoding as edec
import layer1.manchester_encoding as me
import layer2.frame as frame
from layer2.ethernet.ethernet import EthernetFrame
from layer2.ethernet.noneable_data_structures import NoneableBitArray
from layer2.hdlc.hdlc import HdlcFrame
from layer2.hdlc_base import HdlcMode
from layer2.ppp.point_to_point import PppFrame


def create_ethernet_signal(frames: list[EthernetFrame]) -> Callable[[float], float]:
    return me.encode(eenc.encode(frames))


def create_hdlc_signal(frames: list[frame.Frame], *args) -> Callable[[float], float]:
    return me.encode(list(frame.encode(frames, *args)))


def decode_frames_ethernet(signal: Callable[[float], float]) -> list[EthernetFrame]:
    received_bits = NoneableBitArray(me.decode(signal))
    return edec.decode(received_bits)


def decode_frames_hdlc(signal: Callable[[float], float], mode: HdlcMode, extended: bool) -> list[HdlcFrame]:
    received_bits = [x for x in me.decode(signal) if x is not None]
    return frame.decode(BitArray(auto=received_bits), HdlcFrame, mode=mode, extended=extended)


def decode_frames_ppp(signal: Callable[[float], float], mode: HdlcMode) -> list[PppFrame]:
    received_bits = [x for x in me.decode(signal) if x is not None]
    return frame.decode(BitArray(auto=received_bits), PppFrame, mode=mode)
