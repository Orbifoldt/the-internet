from unittest import TestCase

from bitstring import BitArray

from layer3.tools import checksum, int_to_bits, bits_to_int


class Test(TestCase):
    def test_int_to_bits(self):
        self.assertEqual([1, 1, 0, 1], int_to_bits(11))

    def test_bits_to_int(self):
        self.assertEqual(11, bits_to_int([1, 1, 0, 1]))

    def test_checksum(self):
        # example taken from wikipedia, with calculate_checksum bits replaced with vv  vv zeroes
        data = BitArray(auto=b'\x45\x00\x00\x73\x00\x00\x40\x00\x40\x11\x00\x00\xc0\xa8\x00\x01\xc0\xa8\x00\xc7')
        chksum = checksum(data)
        expected = BitArray(uint=0xb861, length=16)
        self.assertEqual(expected, chksum)
