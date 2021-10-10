from abc import ABC, abstractmethod
from enum import Enum

from bitstring import BitArray


class ControlField(ABC):
    @abstractmethod
    def __init__(self, bits: BitArray, pf: bool):
        self.bits = bits
        self.pf = pf

    @property
    def bytes(self):
        return self.bits.bytes


class InformationCf(ControlField):
    ns_bit_length = 3
    nr_bit_length = 3

    def __init__(self, pf: bool, ns: int, nr: int):
        self.ns = BitArray(uint=ns % 2 ** self.ns_bit_length, length=self.ns_bit_length)
        self.nr = BitArray(uint=nr % 2 ** self.nr_bit_length, length=self.nr_bit_length)
        super().__init__(BitArray(auto=[0] + self.ns + [pf] + self.nr), pf)


class ExtendedInfoCf(InformationCf):
    ns_bit_length = 7
    nr_bit_length = 7


class SupervisoryType(Enum):
    RR = 0b00, "Receive Ready"
    REJ = 0b01, "Reject"
    RNR = 0b10, "Receive Not Ready"
    SREJ = 0b11, "Selective Reject"

    def __new__(cls, code, description):
        entry = object.__new__(cls)
        entry.code = entry._value_ = code  # set the value, and the extra attribute
        entry.description = description
        return entry

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: code={self.code!r}; {self.description!r}>'

    @property
    def command(self):
        return True

    @property
    def response(self):
        return True


class SupervisoryCf(ControlField):
    s_type_length = 2
    s_type_bit_length = s_type_length
    nr_bit_length = 3

    def __init__(self, pf: bool, s_type: SupervisoryType, nr: int):
        self.type = s_type
        type_bits = BitArray(uint=s_type.code % 2 ** self.s_type_length, length=self.s_type_bit_length)
        self.nr = BitArray(uint=nr % 2 ** self.nr_bit_length, length=self.nr_bit_length)
        super().__init__(BitArray(auto=[1, 0] + type_bits + [pf] + self.nr), pf)


class ExtendedSupervisoryCf(SupervisoryCf):
    s_type_length = 2
    s_type_bit_length = 6  # to pad with 4 zeroes
    nr_bit_length = 7


class UnnumberedType(Enum):
    SNRM = 0b00, 0b001, True, False, "Set normal response mode"
    SNRME = 0b11, 0b011, True, False, "SNRM extended"
    SARM = 0b11, 0b000, True, False, "Set asynchronous response mode"
    SARME = 0b11, 0b010, True, False, "SARM extended"
    SABM = 0b11, 0b100, True, False, "Set asynchronous balanced mode"
    SABME = 0b11, 0b110, True, False, "SABM extended"
    SM = 0b00, 0b011, True, False, "Set Mode"
    SIM = 0b10, 0b000, True, False, "Set initialization mode"
    RIM = 0b10, 0b000, False, True, "Request initialization mode"
    DISC = 0b00, 0b010, True, False, "Disconnect"
    RD = 0b00, 0b010, False, True, "Request disconnect"
    UA = 0b00, 0b110, False, True, "Unnumbered acknowledgment"
    DM = 0b11, 0b000, False, True, "Disconnect mode"
    UI = 0b00, 0b000, True, True, "Unnumbered information"
    UIH = 0b11, 0b111, True, True, "UI with header check"
    UP = 0b00, 0b100, True, False, "Unnumbered poll"
    RSET = 0b11, 0b001, True, False, "Reset"
    XID = 0b11, 0b101, True, True, "Exchange identification"
    TEST = 0b00, 0b111, True, True, "Test"
    FRMR = 0b10, 0b001, False, True, "Frame reject"
    NR0 = 0b01, 0b000, True, True, "Nonreserved 0"
    NR1 = 0b01, 0b001, True, True, "Nonreserved 1"
    NR2 = 0b01, 0b010, True, True, "Nonreserved 2"
    NR3 = 0b01, 0b011, True, True, "Nonreserved 3"
    AC0 = 0b10, 0b110, True, True, "Ack connectionless, seq 0"
    AC1 = 0b10, 0b111, True, True, "Ack connectionless, seq 1"
    CFGR = 0b10, 0b011, True, True, "Configure for test"
    BCN = 0b11, 0b111, False, True, "Beacon"

    def __new__(cls, m1, m2, command, response, description):
        entry = object.__new__(cls)
        entry._value_ = (m1, m2)
        entry.m1 = m1
        entry.m2 = m2
        entry.command = command
        entry.response = response
        entry.description = description
        return entry

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: code=({self.m1!r},{self.m2!r}); {self.description!r}>'




class UnnumberedCf(ControlField):
    m1_bits = 2
    m2_bits = 3

    def __init__(self, pf: bool, u_type: UnnumberedType):
        self.type = u_type
        self.m1 = BitArray(uint=u_type.m1 % 2 ** self.m1_bits, length=self.m1_bits)
        self.m2 = BitArray(uint=u_type.m2 % 2 ** self.m2_bits, length=self.m2_bits)
        super().__init__(BitArray(auto=[1, 1] + self.m1 + [pf] + self.m2), pf)
