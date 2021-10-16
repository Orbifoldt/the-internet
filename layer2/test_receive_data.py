from unittest import TestCase

from bitstring import BitArray
from layer1 import manchester_encoding as me
from layer2.receive_data import destuff_bits, stuff_bits, encode_with_flag
from receive_data_physical import decode_frame_bits, decode_frame_bytes
from layer2.tools import bits_to_int, bit_to_byte_generator


def bool_list(string: str):
    return [c == '1' for c in string]


class Test(TestCase):
    pattern_str = "11111"
    stuffing_bit = False
    pattern = bool_list(pattern_str)

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

    #####################################
    #      Stuffing and escaping        #
    #####################################

    def test_stuff_bits_single_match(self):
        data = bool_list("1001001101010" + self.pattern_str + "01101101011001110")
        stuffed = stuff_bits(data, self.pattern, stuffing_bit=self.stuffing_bit)
        expected = bool_list("1001001101010" + self.pattern_str + "0" + "01101101011001110")
        self.assertEqual(expected, stuffed)

    def test_stuff_bits_single_match_end_of_list(self):
        data = bool_list(self.pattern_str)
        stuffed = stuff_bits(data, self.pattern, stuffing_bit=self.stuffing_bit)
        expected = bool_list(self.pattern_str + "0")
        self.assertEqual(expected, stuffed)

    def test_stuff_bits_multiple_matches(self):
        some_data = "00"
        data_str = some_data + self.pattern_str + some_data + self.pattern_str + self.pattern_str + some_data + self.pattern_str
        data = bool_list(data_str)

        stuffed = stuff_bits(data, self.pattern, stuffing_bit=self.stuffing_bit)

        stuff_str = self.pattern_str + "0"
        expected = bool_list(some_data + stuff_str + some_data + stuff_str + stuff_str + some_data + stuff_str)
        self.assertEqual(expected, stuffed)

    def test_destuff_bits_single_match(self):
        stuffed_data = bool_list("1001001101010" + self.pattern_str + "0" + "01101101011001110")
        destuffed = destuff_bits(stuffed_data, self.pattern, stuffing_bit=self.stuffing_bit)
        expected = bool_list("1001001101010" + self.pattern_str + "01101101011001110")
        self.assertEqual(expected, destuffed)

    def test_destuff_bits_single_match_end_of_list(self):
        stuffed_data = bool_list(self.pattern_str + "0")
        destuffed = destuff_bits(stuffed_data, self.pattern, stuffing_bit=self.stuffing_bit)
        expected = bool_list(self.pattern_str)
        self.assertEqual(expected, destuffed)

    def test_destuff_bits_multiple_matches(self):
        stuff_str = self.pattern_str + "0"
        some_data = "00011100010"
        stuffed_data_str = some_data + stuff_str + some_data + stuff_str + stuff_str + some_data + stuff_str
        stuffed = bool_list(stuffed_data_str)

        destuffed = destuff_bits(stuffed, bool_list(self.pattern_str), stuffing_bit=self.stuffing_bit)
        expected = bool_list(some_data + self.pattern_str + some_data + self.pattern_str
                             + self.pattern_str + some_data + self.pattern_str)
        self.assertEqual(expected, destuffed)

    #####################################
    #          Encoding frames          #
    #####################################

    def test_encode_with_flag(self):
        flag = b'a'
        data = [b'abc', b'xyz', b'123']
        expected = flag + data[0] + flag + data[1] + flag + data[2] + flag
        self.assertEqual(expected, encode_with_flag(data, flag))
