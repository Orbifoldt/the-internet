from math import sin, pi, cos, floor, ceil
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
    return -node1(t / 2) - node2(t / 2)


def rising_edge_after_falling(t):
    return node1(t / 2) + node2(t / 2)


def starting_rising_edge(t):
    if t < -0.5:
        return 0
    smoothness_factor = 1 if t > -0.4 else cos(10 * pi * t) / 2 + 1 / 2  # (- cos(10 * pi * (t + 0.5)) + 1)/2
    return smoothness_factor * node1(t)


def starting_falling_edge(t):
    return - starting_rising_edge(t)


def final_rising_edge(t):
    if t > 0.5:
        return 0
    smoothness_factor = 1 if t < 0.4 else cos(10 * pi * t) / 2 + 1 / 2
    return smoothness_factor * node1(t)


def final_falling_edge(t):
    return - final_rising_edge(t)


def encode(data: BitArray):
    def f(t):
        if t < -0.5 or t >= len(data) - 0.5:
            return 0
        elif t < 0:
            if data[0] == 1:
                return starting_rising_edge(t)
            else:
                return starting_falling_edge(t)
        elif t >= len(data) - 1:
            if data[:-1] == 1:
                return final_rising_edge(t)
            else:
                return final_falling_edge(t)
        else:
            # n = round(t)
            n = ceil(t)
            if data[n - 1] == 0 and data[n] == 0:
                return falling_edge_after_falling(t - n)
            elif data[n - 1] == 0 and data[n] == 1:
                return rising_edge_after_falling(t - n)
            elif data[n - 1] == 1 and data[n] == 0:
                return falling_edge_after_rising(t - n)
            elif data[n - 1] == 1 and data[n] == 1:
                return rising_edge_after_rising(t - n)
            else:
                raise ValueError("Hallo, doe eens even niet.")

    return f


bits = BitArray(bin="0b10101010101")
ts = np.linspace(-1, len(bits) + 1, len(bits) * 100)
ys = [encode(bits)(t) for t in ts]

fig = plt.figure()
plt.plot(ts, ys, 'b')
plt.show()  # hmmmmm, this could be smoother...
