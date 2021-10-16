from unittest import TestCase

from layer2.escape import EscapeSchema


class TestEscapeSchema(TestCase):
    escape_byte = b'\x00'
    escape_map = {
        b'\x00': b'\xF0',
        b'\x01': b'\xF1'
    }
    escape_schema = EscapeSchema(escape_byte, escape_map)

    def test_cant_create_schema_with_escape_byte_of_len_unequal_to_1(self):
        with self.assertRaises(ValueError):
            EscapeSchema(b'\x00\x01', self.escape_map)

    def test_cant_create_schema_with_non_unique_escape_map_values(self):
        with self.assertRaises(ValueError):
            EscapeSchema(self.escape_byte, {b'\x00': b'\xF0', b'\x01': b'\xF0'})

    def test_escape_char_should_be_escaped_correctly(self):
        data = b'\x00'
        escaped = self.escape_schema.escape(data)
        expected = b'\x00\xF0'
        self.assertEqual(expected, escaped)
        self.assertEqual(b'\x00', data, f"Input '{data}' has gotten mutated.")

    def test_other_char_in_map_should_be_escaped_correctly(self):
        data = b'\x01'
        escaped = self.escape_schema.escape(data)
        expected = b'\x00\xF1'
        self.assertEqual(expected, escaped)

    def test_any_other_char_not_in_map_should_not_be_escaped(self):
        data = b'\x02'
        escaped = self.escape_schema.escape(data)
        expected = b'\x02'
        self.assertEqual(expected, escaped)

    def test_multiple_non_escapable_chars_should_not_be_escaped(self):
        data = b'\x02\xAB\xFF\x99'
        escaped = self.escape_schema.escape(data)
        expected = data
        self.assertEqual(expected, escaped)

    def test_mix_of_escape_and_non_escapable_chars_should_be_escaped_properly(self):
        data = b'\x00\xAA\x01\xF0\xF1\x00\x01'
        escaped = self.escape_schema.escape(data)
        expected = b'\x00\xF0\xAA\x00\xF1\xF0\xF1\x00\xF0\x00\xF1'
        self.assertEqual(expected, escaped)

    def test_escaping_some_ascii_text(self):
        esc_schema = EscapeSchema(b'\x7D', {b'\x7D': b'\x5D', b'\x7E': b'\x5E'})
        information = b'Some information that' + b'\x7E' + b' we send in this frame!'
        escaped_information = b'Some information that' + b'\x7D' + b'\x5E' \
                              + b' we send in this frame!'
        escaped = esc_schema.escape(information)
        self.assertEqual(escaped_information, escaped)

    def test_escape_char_should_be_unescaped_correctly(self):
        data = b'\x00\xF0'
        unescaped = self.escape_schema.unescape(data)
        expected = b'\x00'
        self.assertEqual(expected, unescaped)
        self.assertEqual(b'\x00\xF0', data, f"Input '{data}' has gotten mutated.")

    def test_other_char_in_map_should_be_unescaped_correctly(self):
        data = b'\x00\xF1'
        unescaped = self.escape_schema.unescape(data)
        expected = b'\x01'
        self.assertEqual(expected, unescaped)

    def test_any_other_char_not_in_map_should_not_be_unescaped(self):
        data = b'\x02'
        unescaped = self.escape_schema.unescape(data)
        expected = b'\x02'
        self.assertEqual(expected, unescaped)

    def test_multiple_non_escapable_chars_should_not_be_unescaped(self):
        data = b'\x02\xAB\xFF\x99'
        unescaped = self.escape_schema.unescape(data)
        expected = data
        self.assertEqual(expected, unescaped)

    def test_mix_of_escape_and_non_escapable_chars_should_be_unescaped_properly(self):
        data = b'\x00\xF0\xAA\x00\xF1\xF0\xF1\x00\xF0\x00\xF1'
        unescaped = self.escape_schema.unescape(data)
        expected = b'\x00\xAA\x01\xF0\xF1\x00\x01'
        self.assertEqual(expected, unescaped)

    def test_escape_and_unescape_should_be_identity(self):
        esc_schema = EscapeSchema(b'\x7D', {b'\x7D': b'\x5D', b'\x7E': b'\x5E'})
        data = b'\x68\x61\x74\xbe\x7e\x20\x77\x68\x61\x74\x7d\x5e\x20\x77'
        escaped = esc_schema.escape(data)
        unescaped = esc_schema.unescape(escaped)
        self.assertEqual(data, unescaped)

    def test_escape_with_readable_ascii(self):
        pattern = b'a'
        escape = b'Z'
        esc_schema = EscapeSchema.from_char(byte_to_escape=pattern, escape_char=escape)
        data = b'a sentence with a great many of aaaaaa and a Z or two Z'
        escaped = esc_schema.escape(data)
        expected = b'Za sentence with Za greZat mZany of ZaZaZaZaZaZa Zand Za ZZ or two ZZ'
        self.assertEqual(expected, escaped)

    def test_unescape_bytes_with_readable_ascii(self):
        pattern = b'a'
        escape = b'Z'
        esc_schema = EscapeSchema.from_char(byte_to_escape=pattern, escape_char=escape)
        escaped_data = b'Za sentence with Za greZat mZany of ZaZaZaZaZaZa Zand Za ZZ or two ZZ'
        unescaped = esc_schema.unescape(escaped_data)
        expected = b'a sentence with a great many of aaaaaa and a Z or two Z'
        self.assertEqual(expected, unescaped)

    def test_unproperly_escaped_text_should_not_throw_exception_but_ignore_mistake(self):
        pattern = b'a'
        escape = b'Z'
        esc_schema = EscapeSchema.from_char(byte_to_escape=pattern, escape_char=escape)
        escaped_data = b'These chZarZacters Z Zand a Zare not properly escZaped!'
        unescaped = esc_schema.unescape(escaped_data)
        expected = b'These characters  and a are not properly escaped!'
        self.assertEqual(expected, unescaped)

