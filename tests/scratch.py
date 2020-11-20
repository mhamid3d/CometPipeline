from functools import partial


def f(a, b, c, d, e):
    return a + e

stuff = [1, 2, 3, 4, 5]
print f(*stuff)