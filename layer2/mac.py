import re


class Mac(object):
    mac_pattern = re.compile(r"^(?:[0-9A-Fa-f]{2})([-:])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}$")

    def __init__(self, address: bytes, separator=':', uppercase=False) -> None:
        self.address = bytes(address)
        self.separator = separator
        self.uppercase = uppercase

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


