from __future__ import annotations

from enum import Enum
from ipaddress import IPv4Address
from copy import deepcopy, copy
from typing import Final

from layer2.ethernet.ethernet import EthernetFrame, EtherType
from layer2.mac import Mac


class ARPFrame(EthernetFrame):
    def __init__(self, arp_packet: ARPPacket):
        super().__init__(Mac(arp_packet.target_hw_addr), Mac(arp_packet.sender_hw_addr), arp_packet.bytes,
                         EtherType.ARP)


class ARPOperation(Enum):
    REQUEST = 1
    REPLY = 2

    @property
    def bytes(self):
        return self.value.to_bytes(2, byteorder="big")


class HType(Enum):
    ETHERNET = 1

    @property
    def bytes(self):
        return self.value.to_bytes(2, byteorder="big")


class ARPPacket(object):
    UNKNOWN_MAC: Final = Mac(b'\xff\xff\xff\xff\xff\xff')

    def __init__(self, sender_hw_addr: Mac, sender_protocol_addr: IPv4Address, target_protocol_addr: IPv4Address,
                 target_hw_addr: Mac = UNKNOWN_MAC, htype: HType = HType.ETHERNET, ptype: EtherType = EtherType.IPV4,
                 operation: ARPOperation = ARPOperation.REQUEST):
        self.htype = htype.bytes
        self.ptype = ptype.bytes
        self.hlen = (6).to_bytes(1, byteorder="big")
        self.plen = (4).to_bytes(1, byteorder="big")
        self.operation = operation
        self.sender_mac = Mac(sender_hw_addr.address)
        self.sender_ip = sender_protocol_addr
        self.target_mac = Mac(target_hw_addr.address)
        self.target_ip = target_protocol_addr


    @property
    def bytes(self):
        return self.htype + self.ptype + self.hlen + self.plen + self.operation_bytes + self.sender_hw_addr + \
               self.sender_protocol_addr + self.target_hw_addr + self.target_protocol_addr

    def get_response(self, answer_hw_address: Mac):
        if self.operation_bytes != ARPOperation.REQUEST.bytes:
            raise ValueError("Can only generate a reply to an ARP packet with REQUEST operation.")
        response_packet: ARPPacket = deepcopy(self)
        response_packet.operation = ARPOperation.REPLY
        response_packet.sender_mac = copy(answer_hw_address)
        response_packet.sender_ip = self.target_ip
        response_packet.target_mac = copy(self.sender_mac)
        response_packet.target_ip = self.sender_ip
        return ARPFrame(arp_packet=response_packet)

    @property
    def operation_bytes(self):
        return self.operation.bytes

    @property
    def target_hw_addr(self):
        return self.target_mac.address

    @property
    def sender_hw_addr(self):
        return self.sender_mac.address

    @property
    def sender_protocol_addr(self):
        return int(self.sender_ip).to_bytes(4, byteorder="big")

    @property
    def target_protocol_addr(self):
        return int(self.target_ip).to_bytes(4, byteorder="big")

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.bytes == other.bytes


def extract_arp_packet(frame: EthernetFrame):
    if not frame.ether_type == EtherType.ARP:
        raise ValueError("Ether type of provided frame is not ARP")
    htype = HType(int.from_bytes(frame.payload[0:2], byteorder='big'))
    ptype = EtherType(int.from_bytes(frame.payload[2:4], byteorder='big'))
    hlen = int.from_bytes(frame.payload[4:5], byteorder='big')
    plen = int.from_bytes(frame.payload[5:6], byteorder='big')
    operation = ARPOperation(int.from_bytes(frame.payload[6:8], byteorder='big'))
    sender_hw_addr = Mac(frame.payload[8:14])
    sender_protocol_addr = IPv4Address(int.from_bytes(frame.payload[14:18], byteorder='big'))
    target_hw_addr = Mac(frame.payload[18:24])
    target_protocol_addr = IPv4Address(int.from_bytes(frame.payload[24:28], byteorder='big'))

    if htype != HType.ETHERNET:
        raise ValueError("ARP only implemented for ethernet hardware type")
    if ptype != EtherType.IPV4:
        raise ValueError("ARP only implemented for IPv4 protocol")
    if hlen != 6:
        raise ValueError(f"Hardware address length for ethernet should be 6, but received {hlen}")
    if plen != 4:
        raise ValueError(f"Protocol address length for IPv4 should be 4, but received {plen}")

    return ARPPacket(sender_hw_addr, sender_protocol_addr, target_protocol_addr, target_hw_addr, htype, ptype,
                     operation)
