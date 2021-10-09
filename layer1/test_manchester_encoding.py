from unittest import TestCase
from bitstring import BitArray
from manchester_encoding import encode, decode


class Test(TestCase):

    def test_encode(self):
        bit_array = BitArray(bin="0b1001001010111100001010101011101010010011000101111100000010000111")
        signal = encode(bit_array)
        epsilon = 0.01
        for i in range(len(bit_array)):
            expected_bit = bit_array[i]
            found_bit = (signal(i + epsilon) - signal(i - epsilon)) > 0
            self.assertEqual(found_bit, expected_bit, msg=f"Found '{found_bit}', expected {i}-th bit='{expected_bit}'")

    def test_decode(self):
        bit_array = BitArray(bin="0b10010101101011111100011001001101010000011111110011011001110001110")
        signal = encode(bit_array)
        decoded = decode(signal)
        for i in range(len(bit_array)):
            bit = next(decoded)
            self.assertEqual(bit, bit_array[i])

