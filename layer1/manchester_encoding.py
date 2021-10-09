from itertools import count
from math import sin, pi, cos, floor, ceil
from typing import Callable, Generator

import numpy as np
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
    """
    Given a physical signal this will return a generator that will contain the bits encoded in that signal
    It assumes the Manchester code is used for encoding the bits (i.e. a rising edge is 1, a falling edge is 0)
    If the signal is 0 during an extended period of time this is detected and the generator is closed
    :param signal: (float) -> float : the signal containing the manchester encoded bits with a frequency = 1,
    i.e. the signal is polled at integer values.
    :return: Generator containing either None if no signal was seen, or a bool representing the bit value (according
    to manchester encoding)
    """
    epsilon = 0.001
    signal_started = False
    for j in count():
        y1 = signal(j - epsilon)
        y2 = signal(j + epsilon)
        if y1 == 0. and y2 == 0.:
            if signal_started:
                signal_dead = True
                for x in np.linspace(j + epsilon, j + 96, 173):
                    if signal(x) != 0:
                        signal_dead = False
                        break
                if signal_dead:
                    return
            yield None
        else:
            signal_started = True
            yield y2 > y1


# TODO: create jupyter nb with below
# import matplotlib.pyplot as plt
# import numpy as np
# bits = BitArray(bin="0b1001001001010101")
# ts = np.linspace(-1, len(bits) + 1, len(bits) * 100)
# ys = [encode(bits)(t) for t in ts]
#
# fig = plt.figure()
# plt.plot(ts, ys, 'b')
# plt.show()
