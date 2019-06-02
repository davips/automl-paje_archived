import random

from math import floor


def exponential_integers(kmax, kmin=1, only_odd=True, exponent=1.5):
    """
    Generates a list of odd ks increasing exponentially according to x^1.5:
        [1, 3, 5, 9, 11, 15, 19, ..., 37, 43, 47, 53, ..., 83, 89, 97, 103,
        ..., 955, 971, 985, ...]
    :param kmax: maximum allowed number
    :param only_odd: odd numbers only
    :param exponent: level of increase
    :return: list of numbers
    """
    ks = [floor(pow(kmin, 1 / exponent))]
    for x in list(range(ks[0] + 1,
                        floor(pow(kmax, 1 / exponent)))):
        k = round(pow(x, exponent))
        ks.append(k + 1 if only_odd and k % 2 == 0 else k)
    return ks


def sample(kind, interval=None):
    """
    Handles sampling according to the given type.
    :param kind:
    :param interval:
    :return:
    """
    if interval is None:
        raise Exception("'kind '" + kind + "' missing a list interval values!")
    # TODO: Add parameter to customize sampling strategy.
    try:
        if kind == 'c': return categoric_sample(interval)
        if kind == 'o': return ordinal_sample(interval)
        if kind == 'r': return real_sample(interval[0], interval[1])
        if kind == 'z': return integer_sample(interval[0], interval[1])
    except Exception as e:
        print(kind, interval)
        raise SamplingException(e)

    raise Exception('Unknown kind of interval: ', kind,
                    ' Interval: ', interval)


def categoric_sample(values):
    return random.choice(values)


def integer_sample(min, max):
    return random.randint(min, max + 1)


def ordinal_sample(values):
    return random.choice(values)


def real_sample(min, max):
    return ((max - min) * random.random()) + min


class SamplingException(Exception):
    pass
