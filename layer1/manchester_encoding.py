from itertools import count
from math import sin, pi, cos, floor, ceil
from typing import Callable, Generator
from bitstring import BitArray


def node1(t):
    return sin(2 * pi * t)


def node2(t):
    return 1 / 3 * node1(3 * t)


def same_phase(t):
    return node1(t)


def switch_phase(t):
    return node1(t / 2) + node2(t / 2)


def start_smoothing(t):
    if t < -0.5:
        return 0.
    elif t >= -0.4:
        return 1.
    else:
        return cos(10 * pi * t) / 2 + 1 / 2


def end_smoothing(t):
    return start_smoothing(-t)


def sign(bit):
    return 1 if bit else -1


def encode_segment(t, previous_bit, current_bit):
    if t < -1 or t >= 0:
        return 0.
    sgn = sign(current_bit)
    if previous_bit == current_bit:
        return sgn * same_phase(t)
    else:
        return sgn * switch_phase(t)


def encode_boundary(t, current_bit, start):
    if start:
        return sign(current_bit) * start_smoothing(t) * node1(t)
    else:
        return sign(current_bit) * end_smoothing(t) * node1(t)


def encode(data: BitArray) -> Callable[[float], float]:
    def signal(t):
        n = len(data)
        if t < -0.5 or t >= n - 0.5:
            return 0.
        elif 0 <= t < n - 1:
            k = ceil(t)
            return encode_segment(t - k, data[k - 1], data[k])
        else:  # -0.5 <= t < 0, or n-1 <= t < n-0.5
            return encode_boundary(t - ceil(t), data[round(t)], start=(t < 0))

    return signal


def decode(signal: Callable[[float], float]) -> Generator[bool, None, None]:
    epsilon = 0.001
    for j in count():
        yield signal(j + epsilon) > signal(j - epsilon)





# import matplotlib.pyplot as plt
# import numpy as np
# bits = BitArray(bin="0b1001001001010101")
# ts = np.linspace(-1, len(bits) + 1, len(bits) * 100)
# ys = [encode(bits)(t) for t in ts]
#
# fig = plt.figure()
# plt.plot(ts, ys, 'b')
# plt.show()
