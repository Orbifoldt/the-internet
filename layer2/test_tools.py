from unittest import TestCase

from bitstring import BitArray

from layer2.tools import bits_to_int, bit_to_byte_generator, crc32, find_match, replace_all_matches, \
    bits_to_bytes, interleave, separate, get_data_between_flags


def bool_list(string: str):
    return [c == '1' for c in string]


class Test(TestCase):
    def test_crc32(self):
        test_string = b'According to all known laws of aviation...'
        checksum = crc32(test_string)
        self.assertEqual(0xE7CCFC9A.to_bytes(4, byteorder='little'), checksum)

    def test_bits_to_int(self):
        self.assertEqual(0, bits_to_int([]))
        self.assertEqual(0, bits_to_int([False, False, False]))
        self.assertEqual(1, bits_to_int([True]))
        self.assertEqual(1, bits_to_int([False, False, False, False, True]))
        self.assertEqual(17, bits_to_int([True, False, False, False, True]))
        self.assertEqual(17, bits_to_int([False, False, False, True, False, False, False, True]))

    def test_bits_to_bytes(self):
        binary = "010101000110100001101001011100110010000001101001011100110010000001110011011011110110110101100101001" \
                 "000000100000101010011010000110100100101001001001000000111010001100101011110000111010000100001"
        extracted_bytes = bits_to_bytes(bool_list(binary))
        expected = b'This is some ASCII text!'
        self.assertEqual(expected, extracted_bytes)

    def test_bit_to_byte_generator(self):
        bits = BitArray(bin="01010001" + "00100100" + "111")
        src = (b for b in bits)
        byte_src = bit_to_byte_generator(src)
        found_bytes = [b for b in byte_src]
        self.assertEqual(81, found_bytes[0])
        self.assertEqual(36, found_bytes[1])
        self.assertEqual(224, found_bytes[2])

    def test_find_match(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        pattern = [3, 4, 5]
        self.assertEqual(2, find_match(data, pattern))
        self.assertEqual(2, find_match(data, pattern, 2))

    def test_find_match_singleton(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        pattern = [6]
        self.assertEqual(5, find_match(data, pattern))
        self.assertEqual(5, find_match(data, pattern, 4))

    def test_find_match_start_of_list(self):
        data = [3, 4, 5, 6, 7, 8, 9, 0]
        pattern = [3, 4, 5]
        self.assertEqual(0, find_match(data, pattern))

    def test_find_match_end_of_list(self):
        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        pattern = [6, 7, 8, 9]
        self.assertEqual(6, find_match(data, pattern))

    def test_find_match_no_matches(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        pattern = [3, 6, 1]
        self.assertIsNone(find_match(data, pattern))

    def test_find_match_empty_list_should_return_none(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        pattern = []
        self.assertIsNone(find_match(data, pattern))

    def test_find_match_multiple_matches(self):
        data = [1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 8, 9, 0]
        pattern = [3, 4, 5]
        self.assertEqual(2, find_match(data, pattern))
        self.assertEqual(2, find_match(data, pattern, 2))
        self.assertEqual(7, find_match(data, pattern, 4))

    def test_find_match_with_escape(self):
        data = [1, 2, 0, 3, 4, 5, 6, 0, 7, 3, 4, 5, 8, 9, 0]
        pattern = [3, 4, 5]
        escape = [0]
        self.assertEqual(9, find_match(data, pattern, start_idx=0, escape=escape))
        self.assertEqual(9, find_match(data, pattern, start_idx=2, escape=escape))
        self.assertEqual(9, find_match(data, pattern, start_idx=2, escape=escape))

    def test_replace_all_matches(self):
        data = [1, 2, 3, 4, 6, 3, 7, 4, 3, 4, 5, 8, 9, 0, 3, 4]
        pattern = [3, 4]
        replacement = [8, 8, 8, 8]
        expected = [1, 2, 8, 8, 8, 8, 6, 3, 7, 4, 8, 8, 8, 8, 5, 8, 9, 0, 8, 8, 8, 8]
        self.assertEqual(expected, replace_all_matches(data, pattern, replacement))

    def test_interleave(self):
        self.assertEqual([0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0], interleave([1, 2, 3, 4, 5], 0))

    def test_get_data_between_flags(self):
        start = [1, 2]
        end = [8, 9]
        block1 = [5, 5, 5]
        block2 = [6, 6, 6]
        data = [0, 0, 0] + start + block1 + end + [-1, -1] + start + block2 + end + [0, 0]
        found = get_data_between_flags(data, start, end)
        self.assertEqual((block1, 3, 8), found)

    def test_separate(self):
        start = [1, 2]
        end = [8, 9]
        block1 = [5, 6, 7]
        block2 = [7, 6, 5]
        data = [0] + start + block1 + end + [0, 0] + start + block2 + end + [0, 0]
        separated = separate(data, start, end)
        self.assertEqual(2, len(separated))
        self.assertListEqual(block1, separated[0])
        self.assertListEqual(block2, separated[1])

    def test_separate_with_repeated_start(self):
        start = [1, 2]
        end = [8, 9]
        block1 = [5, 6, 7] + start + [5, 6, 7]
        block2 = [7, 6, 5]
        data = [0] + start + block1 + end + [0, 0] + start + block2 + end + [0, 0]
        separated = separate(data, start, end)
        self.assertEqual(2, len(separated))
        self.assertListEqual(block1, separated[0])
        self.assertListEqual(block2, separated[1])

    def test_separate_with_equal_start_and_end_flags(self):
        start = [1, 2]
        block1 = [5, 6, 7]
        block2 = [7, 6, 5]
        data = [0] + start + block1 + start + [0, 0] + start + block2 + start + [0, 0]
        separated = separate(data, start)
        self.assertEqual(3, len(separated))
        self.assertListEqual(block1, separated[0])
        self.assertListEqual([0, 0], separated[1])
        self.assertListEqual(block2, separated[2])
