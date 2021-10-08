from math import sin, pi, cos
import matplotlib.pyplot as plt
import numpy as np

from bitstring import BitArray


def node1(t):
    return sin(2 * pi * t)


def node2(t):
    return 1 / 3 * node1(3 * t)


def rising_edge_after_rising(t):
    return node1(t)


def falling_edge_after_falling(t):
    return - node1(t)


def falling_edge_after_rising(t):
    return node1(t) + node2(t)  # this is wrong, should be t/2 ? but then smooth...


def rising_edge_after_falling(t):
    return - node1(t) - node2(t)


def starting_rising_edge(t):
    if t < -0.5:
        return 0
    smoothness_factor = 1 if t > -0.4 else cos(10 * pi * t) / 2 + 1 / 2  # (- cos(10 * pi * (t + 0.5)) + 1)/2
    return smoothness_factor * node1(t)


def starting_falling_edge(t):
    return - starting_rising_edge(t)


def encode(data: BitArray):
    def f(t):
        n = round(t)
        if n < 0 or n >= len(data):
            return 0
        elif n == 0:
            if data[0] == 1:
                return starting_rising_edge(t)
            else:
                return starting_falling_edge(t)
        else:
            if data[n - 1] == 0 and data[n] == 0:
                return falling_edge_after_falling(t)
            elif data[n - 1] == 0 and data[n] == 1:
                return rising_edge_after_falling(t)
            elif data[n - 1] == 1 and data[n] == 0:
                return falling_edge_after_rising(t)
            elif data[n - 1] == 1 and data[n] == 1:
                return rising_edge_after_rising(t)
            else:
                raise ValueError("Hallo, doe eens even niet.")

    return f


bits = BitArray(bin="0b1010101")
ts = np.linspace(-1, len(bits), len(bits) * 100)
ys = [encode(bits)(t) for t in ts]


fig = plt.figure()
plt.plot(ts, ys, 'b')
plt.show()  # hmmmmm, this could be smoother...
