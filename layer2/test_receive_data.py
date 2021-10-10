from unittest import TestCase

from bitstring import BitArray
from layer1 import manchester_encoding as me
from receive_data import decode_frame_bits, decode_frame_bytes
from layer2.tools import bits_to_int, bit_to_byte_generator


class Test(TestCase):
    def test_decode_frame_bits(self):
        start = "10101011"
        end = "01111110"
        data = "0101111101000110010011010100000111110011011001110001110"
        bit_array = BitArray(bin=start + data + end)
        signal = me.encode(bit_array)
        decoded = decode_frame_bits(signal, start_flag=BitArray(bin=start), end_flag=BitArray(bin=end))
        self.assertEqual(data, decoded.bin)

    def test_decode_frame_bits_with_start_noise(self):
        noise = "1010101010101010101010101010100"
        start = "101011"
        end = "0111111110"
        data = "1010111110100011001001110101010101010010100001111100110110011100011101"
        bit_array = BitArray(bin=noise + start + data + end)
        signal = me.encode(bit_array)
        decoded = decode_frame_bits(signal, start_flag=BitArray(bin=start), end_flag=BitArray(bin=end))
        self.assertEqual(data, decoded.bin)

    def test_decode_frame_bits_with_end_noise(self):
        noise = "10100000010101010101010000101"
        start = "101011"
        end = "10111111101"
        data = "000101111101000110010011010100000111110011011001110001110000"
        bit_array = BitArray(bin=start + data + end + noise)
        signal = me.encode(bit_array)
        decoded = decode_frame_bits(signal, start_flag=BitArray(bin=start), end_flag=BitArray(bin=end))
        self.assertEqual(data, decoded.bin)

    def test_decode_frame_bits_without_end_flag(self):
        start = "10101011"
        data = "0101111101000110010011010100000111110011011001110001110"
        bit_array = BitArray(bin=start + data)
        signal = me.encode(bit_array)
        decoded = decode_frame_bits(signal, start_flag=BitArray(bin=start), end_flag=None)
        self.assertEqual(data, decoded.bin)

    def test_decode_frame_bits_without_end_flag_with_noise(self):
        noise = "10100000010101010101010000101"
        start = "10101011"
        data = "010111001101000110010011010100000111110011011001110001110"
        bit_array = BitArray(bin=noise + start + data)
        signal = me.encode(bit_array)
        decoded = decode_frame_bits(signal, start_flag=BitArray(bin=start), end_flag=None)
        self.assertEqual(data, decoded.bin)

    def test_decode_frame_bits_with_escape(self):
        start = "10101011"
        end = "01111110"
        escape = "10111110"
        data1 = "01011111010001100100110101000"
        data2 = "00111110011011001110001110"
        bit_array = BitArray(bin=start + data1 + escape + end + data2 + end)
        signal = me.encode(bit_array)
        decoded = decode_frame_bits(signal, BitArray(bin=start), BitArray(bin=end), escape=BitArray(bin=escape))
        self.assertEqual(data1 + end + data2, decoded.bin)

    def test_decode_frame_bytes_with_escape(self):
        flag = b'\x7E'
        escape = b'\x7D'
        data1 = b'\xA1\xB9\x7D\xAA\x93'
        data2 = b'\x10\x9E\x4F'
        bit_noise = BitArray(bin="010101101010")  # noise that is not multiple of 8 bits
        escaped_data = data1 + escape + flag + data2

        signal = me.encode(bit_noise + BitArray(auto=flag + escaped_data + flag) + bit_noise)
        decoded = decode_frame_bytes(signal, start_flag=flag, end_flag=flag, escape=escape)
        self.assertEqual(data1 + flag + data2, decoded)
