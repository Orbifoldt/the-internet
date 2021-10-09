from unittest import TestCase

from bitstring import BitArray
from layer1 import manchester_encoding as me
from receive_data import decode_to_bits


class Test(TestCase):
    def test_decode_to_bits(self):
        start = "10101011"
        end = "01111110"
        data = "0101111101000110010011010100000111110011011001110001110"
        bit_array = BitArray(bin="0b" + start + data + end)
        signal = me.encode(bit_array)
        decoded = decode_to_bits(signal, start_flag=BitArray(bin="0b" + start), end_flag=BitArray(bin="0b" + end))
        self.assertEqual(data, decoded.bin)

    def test_decode_to_bits_with_start_noise(self):
        noise = "1010101010101010101010101010100"
        start = "101011"
        end = "0111111110"
        data = "1010111110100011001001110101010101010010100001111100110110011100011101"
        bit_array = BitArray(bin="0b" + noise + start + data + end)
        signal = me.encode(bit_array)
        decoded = decode_to_bits(signal, start_flag=BitArray(bin="0b" + start), end_flag=BitArray(bin="0b" + end))
        self.assertEqual(data, decoded.bin)

    def test_decode_to_bits_with_end_noise(self):
        noise = "10100000010101010101010000101"
        start = "101011"
        end = "10111111101"
        data = "000101111101000110010011010100000111110011011001110001110000"
        bit_array = BitArray(bin="0b" + start + data + end + noise)
        signal = me.encode(bit_array)
        decoded = decode_to_bits(signal, start_flag=BitArray(bin="0b" + start), end_flag=BitArray(bin="0b" + end))
        self.assertEqual(data, decoded.bin)
