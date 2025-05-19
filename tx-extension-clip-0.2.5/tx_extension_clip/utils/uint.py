import numpy


def uint64_to_int64(as_uint64: int):
    """
    Returns the int64 number represented by the same byte representation as the the
    provided integer if it was understood to be a uint64 value.
    """
    return numpy.uint64(as_uint64).astype(numpy.int64).item()


def int64_to_uint64(as_int64: int):
    """
    Returns the uint64 number represented by the same byte representation as the the
    provided integer if it was understood to be a int64 value.
    """
    return numpy.int64(as_int64).astype(numpy.uint64).item()
