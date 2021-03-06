import os
import re


class Mac(object):
    mac_pattern = re.compile(r"^(?:[0-9A-Fa-f]{2})([-:])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}$")

    def __init__(self, address: bytes = None, separator=':', uppercase=False) -> None:
        if address is None:
            address = os.urandom(6)
        if len(address) != 6:
            raise ValueError(f"A mac address consists of exactly 6 bytes, got {len(address)} instead.")
        self._address = bytes(address)
        self.separator = separator
        self.uppercase = uppercase

    @property
    def address(self):
        return self._address

    @staticmethod
    def fromstring(mac_string: str):
        if not Mac.mac_pattern.match(mac_string):
            raise ValueError("mac_string should match Mac.mac_pattern")
        return Mac(bytes.fromhex(mac_string.replace(':', '').replace('-', '')))

    def __str__(self) -> str:
        string = self.address.hex(self.separator)
        return string.upper() if self.uppercase else string

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Mac) and self.address == o.address

    def __hash__(self):
        return self.address.__hash__()

    def __copy__(self):
        return Mac(self.address)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()





