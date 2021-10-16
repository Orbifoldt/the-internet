class EscapeSchema(object):
    def __init__(self, escape_byte: bytes, replacement_map: dict[bytes, bytes]):
        self._validate_input(escape_byte, replacement_map)
        self.escape_byte = escape_byte
        self.escape_map = replacement_map
        self._unescape_map = self._build_unescape_map(replacement_map)

    @staticmethod
    def _validate_input(escape_byte: bytes, replacement_map: dict[bytes, bytes]):
        if len(escape_byte) != 1:
            raise ValueError("Escape byte should be a single byte")
        values_set = set()
        map_values_unique = not any(i in values_set or values_set.add(i) for i in replacement_map.values())
        if not map_values_unique:
            raise ValueError("All values of the replacement_map must be unique (else we cant unescape)!")

    @staticmethod
    def _build_unescape_map(replacement_map: dict[bytes, bytes]) -> dict[bytes]:
        return {replacement_map[x]: x for x in replacement_map.keys()}

    @staticmethod
    def from_char(byte_to_escape: bytes, escape_char: bytes):
        return EscapeSchema(escape_char, {escape_char: escape_char, byte_to_escape: byte_to_escape})

    def escape(self, data: bytes) -> bytes:
        escaped = bytes()
        for i in range(len(data)):
            if (current := data[i:i + 1]) in self.escape_map.keys():
                escaped += self.escape_byte + self.escape_map[current]
            else:
                escaped += current
        return escaped

    def _safe_unescape_char(self, char: bytes):
        try:
            return self._unescape_map[char]
        except KeyError as e:
            print("WARNING! Provided data was not properly escaped")
            return char

    def unescape(self, data: bytes) -> bytes:
        unescaped = bytes()
        i = 0
        while i < len(data):
            if (current := data[i:i + 1]) == self.escape_byte:
                unescaped += self._safe_unescape_char(data[i + 1:i + 2])
                i += 1
            else:
                unescaped += current
            i += 1
        return unescaped
