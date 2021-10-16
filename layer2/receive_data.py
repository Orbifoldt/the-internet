from typing import TypeVar

T = TypeVar('T')


# def get_data_after_match(data: list[T], pattern: list[T]) -> Tuple[list[T], int]:
#     if (i := find_match(data, pattern)) is None:
#         raise ValueError("Pattern not found")
#     return data[i + len(pattern):], i + len(pattern)
#
#
# def get_data_until_match(data: list[T], pattern: list[T], escape: list[T] = None) -> Tuple[list[T], int]:
#     if (i := find_match(data, pattern, start_idx=0, escape=escape)) is None:
#         raise ValueError("Pattern not found")
#     return data[:i], i
#
#
# def get_data_until_signal_dead(data: list[T], n: int = 10) -> Tuple[list[T], int]:
#     return get_data_until_match(data, [None] * n)
#
#
# # def get_data_bytes_until_signal_dead(source: Generator[int, None, None]) -> bytes:
# #     return bytes(source)
#
#
# def decode_frame_bits(frame_bits: BitArray, start_flag: BitArray,
#                       end_flag: BitArray = None, escape: BitArray = None) -> BitArray:
#     # decoded = me.decode(signal)
#     get_data_after_match(decoded, pattern=list(start_flag))
#
#     if end_flag is not None:
#         data = get_data_until_match(decoded, list(end_flag), escape)
#         return BitArray(auto=data)
#     else:
#         return get_data_until_signal_dead(decoded)
#
#
# def decode_frame_bytes(signal: Callable[[float], float], start_flag: bytes,
#                        end_flag: bytes = None, escape: bytes = None) -> bytes:
#     decoded = me.decode(signal)
#     get_data_after_match(decoded, list(BitArray(auto=start_flag)))
#
#     byte_source = bit_to_byte_generator(source=decoded)
#     if end_flag is not None:
#         if escape is not None:
#             escape = list(escape)
#         data = get_data_until_match(byte_source, list(end_flag), escape)
#         return bytes(data)
#     else:
#         return get_data_bytes_until_signal_dead(byte_source)
