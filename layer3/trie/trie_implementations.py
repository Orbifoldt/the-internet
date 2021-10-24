from typing import List, Generic, TypeVar

from layer3.trie.trie import AbstractGenericTrie

V = TypeVar('V')


class BinaryGenericTrie(Generic[V], AbstractGenericTrie[int, List[int], V]):
    """
    Trie implementation with integer keys, whose vertices correspond to the binary representation of those keys. The
    root corresponds to the "empty" integer '[]', and in general the n-th layer of this tree corresponds to the n-th
    bit of the key, e.g. layer 1 corresponds to the 1st bit (the 2^0 bit), layer 2 to 2nd bit (2^1), etc.

    Note that this might be a bit of weird implementation, e.g. here 13 is a descendant of 5 because their first 3 bits
    are the same. Often you want to use fixed-width binary representation in a reverse order to have an interpretation
    as addresses and descendants being sub-addresses (e.g. IP or memory addresses). For this see the implementation
    ReversedKeyBinaryGenericTrie32.
    """
    def __init__(self, root_value: V = None):
        super().__init__(root_value)

    @staticmethod
    def pre_processor(key: int | List[int]) -> List[int]:
        if isinstance(key, int):
            return int_to_bits(key)
        return key

    @staticmethod
    def post_processor(internal_key: List[int]) -> int:
        return bits_to_int(internal_key)


def int_to_bits(n: int) -> List[int]:
    bits = []
    remainder = n
    while True:
        bit_i = remainder & 1
        bits.append(bit_i)
        remainder = remainder >> 1
        if remainder == 0:
            break
    return bits


def bits_to_int(bits: List[int]) -> int:
    x = 0
    for bit in reversed(bits):
        x = (x << 1) | bit
    return x


class ReversedKeyBinaryGenericTrie32(Generic[V], AbstractGenericTrie[int, List[int], V]):
    """
    Trie with 32 bit integer keys in reverse order, i.e. the 1st layer below the root corresponds to the 32nd bit with
    lower layers corresponding to the lower bits.
    """
    def __init__(self, root_value: V = None):
        super().__init__(root_value)

    @staticmethod
    def pre_processor(key: int | List[int]) -> List[int]:
        num_bits = 32
        if isinstance(key, int):
            bits = []
            for k in range(num_bits - 1, -1, -1):
                bits.append((key >> k) & 1)
            return bits
        return key

    @staticmethod
    def post_processor(internal_key: List[int]) -> int:
        x = 0
        for bit in internal_key:
            x = (x << 1) | bit
        return x


class StringGenericTrie(Generic[V], AbstractGenericTrie[str, List[str], V]):
    """
    A trie implementation with string keys. The root corresponds to the empty string '', and the n-th layer corresponds
    to the n-th character of the string (reading from left to right). This can for example be used for autocorrection,
    the trie can give the closest matching words to an incomplete word (the values of the nodes can be weights).
    """
    def __init__(self, root_value: V = None):
        super().__init__(root_value)

    @staticmethod
    def pre_processor(key: str | List[str]) -> List[str]:
        return key  # string supports slicing etc, so this can just be the identity map

    @staticmethod
    def post_processor(internal_key: List[str]) -> str:
        return ''.join(internal_key)


