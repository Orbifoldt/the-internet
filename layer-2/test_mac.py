from unittest import TestCase
from mac import *


class TestMac(TestCase):

    def test_constructor(self):
        test_mac = Mac(b'\x1e\xa1\xd6\x9d\x23\x53')
        self.assertEqual(test_mac.address, b'\x1e\xa1\xd6\x9d\x23\x53')
        self.assertEqual(test_mac.__str__(), "1e:a1:d6:9d:23:53")

    def test_fromstring(self):
        test_mac = Mac.fromstring("a1:b2:c3:d4:e5:f6")
        self.assertEqual(test_mac.address, b'\xa1\xb2\xc3\xd4\xe5\xf6')

    def test_fromstring_capitals(self):
        test_mac = Mac.fromstring("A1:B2:C3:D4:E5:F6")
        self.assertEqual(test_mac.address, b'\xa1\xb2\xc3\xd4\xe5\xf6')

    def test_fromstringWithDashes(self):
        test_mac = Mac.fromstring("A1-B2-C3-D4-E5-F6")
        self.assertEqual(test_mac.address, b'\xa1\xb2\xc3\xd4\xe5\xf6')

    def test_other_separator(self):
        test_mac = Mac(b'\xa1\xb2\xc3\xd4\xe5\xf6', separator='-')
        self.assertEqual(test_mac.__str__(), "a1-b2-c3-d4-e5-f6")

    def test_capital(self):
        test_mac = Mac(b'\xa1\xb2\xc3\xd4\xe5\xf6', uppercase=True)
        self.assertEqual(test_mac.__str__(), "A1:B2:C3:D4:E5:F6")
