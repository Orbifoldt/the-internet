import builtins
from abc import ABC, abstractmethod
from typing import Union

from bitstring import BitArray

from layer2.tools import interleave, reduce_bits, reduce_bytes, separate


class Frame(ABC):
    @property
    @abstractmethod
    def flag(self) -> bytes:
        raise NotImplementedError

    @property
    @abstractmethod
    def flag_bits(self) -> BitArray:
        raise NotImplementedError
        # return BitArray(auto=self.flag)

    @abstractmethod
    def bytes(self) -> bytes:
        raise NotImplementedError

    def bits(self) -> BitArray:
        return BitArray(auto=self.bytes())

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and o.bytes() == self.bytes()

    # ENCODING

    def encode_as_bytes(self, *args):
        """ Encoding the bytes of this Frame by means of byte-stuffing/escaping """
        raise NotImplementedError

    def encode_as_bits(self, *args):
        """ Encoding the bits of this Frame by means of bit- or byte-stuffing """
        raise NotImplementedError

    # DECODING

    @classmethod
    def separate_frames(cls, data: BitArray) -> list[BitArray]:
        """Separate data into blocks separated by the class' flag """
        return [BitArray(auto=x) for x in separate(list(data), list(cls.flag_bits))]

    @classmethod
    def safe_extract_frames(cls, decoded_frame_bytes: list[bytes], **kwargs) -> list:
        """
        Decode a Frame for each element of frames_bytes, or drop it if an error occurs.
        """
        received_frames = []
        for decoded in decoded_frame_bytes:
            try:
                frame = cls.interpret_frame_from_bytes(decoded, **kwargs)
                received_frames.append(frame)
            except ValueError as e:
                print(f"Error while receiving frame: {e}. It will be dropped.")
        return received_frames

    @classmethod
    @abstractmethod
    def decode_from(cls, encoded: Union[builtins.bytes, BitArray], **kwargs):
        """ Decoding the bytes corresponding to a single Frame by means of destuffing/unescaping bytes """
        raise NotImplementedError

    # @classmethod
    # @abstractmethod
    # def decode_from_bits(cls, encoded_bits: BitArray) -> builtins.bytes:
    #     """ Decoding the bytes corresponding to a single Frame by means of destuffing/unescaping bytes """
    #     raise NotImplementedError

    @classmethod
    @abstractmethod
    def interpret_frame_from_bytes(cls, decoded_bytes: bytes, **kwargs):
        """ Construct a single Frame from the decoded_bytes """
        raise NotImplementedError


def encode(frames: list[Frame], *args) -> BitArray:
    """
    Generic method for encoding multiple frames into a single "bit-stream" (BitArray in this case). This makes use of
    the frames' own encode_as_bits() methods. The encoded bits of the frames are then interleaved with the Frames' flag
    :return: A single BitArray of the concatenated bits of the frames separated by the flags
    """
    if len(frames) == 0:
        return BitArray()
    encoded_frames = [frame.encode_as_bits(*args) for frame in frames]
    marked_frame_boundaries = interleave(encoded_frames, frames[0].flag_bits)
    return reduce_bits(marked_frame_boundaries)


def encode_bytes(frames: list[Frame], *args) -> bytes:
    if len(frames) == 0:
        return bytes()
    encoded_frames = [frame.encode_as_bytes(*args) for frame in frames]
    marked_frame_boundaries = interleave(encoded_frames, frames[0].flag)
    return reduce_bytes(marked_frame_boundaries)


def decode(data: BitArray, frame_type: Frame.__class__, **kwargs) -> list[Frame]:
    bit_sections = frame_type.separate_frames(data)
    decoded_bytes = [frame_type.decode_from(section, **kwargs) for section in bit_sections]
    return frame_type.safe_extract_frames(decoded_bytes, **kwargs)


def decode_bytes(data: bytes, frame_type: Frame.__class__, **kwargs) -> list[Frame]:
    return decode(BitArray(auto=data), frame_type, **kwargs)

