"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This is an original file from the repo.
We did not make any change to it in final project.
"""

import math

def format_number(n, accuracy=6):
    """
    Formats a number in a user-friendly manner by removing trailing zeros and unnecessary decimal points.

    Args:
        n (float or int): The number to format.
        accuracy (int, optional): The number of decimal places to include. Defaults to 6.

    Returns:
        str: The formatted number as a string.
    """
    fs = "%." + str(accuracy) + "f"  # Create a format string with the specified accuracy
    str_n = fs % float(n)  # Format the number to a string with the given accuracy
    if '.' in str_n:
        str_n = str_n.rstrip('0').rstrip('.')  # Remove trailing zeros and the decimal point if necessary
    if str_n == "-0":
        str_n = "0"  # Replace "-0" with "0" to avoid negative zero representation
    #str_n = str_n.replace("-0", "0")
    return str_n


def lerp(a, b, i):
    """
    Performs linear interpolation between two values.

    Args:
        a (float): The starting value.
        b (float): The ending value.
        i (float): The interpolation factor (0.0 to 1.0).

    Returns:
        float: The interpolated value.
    """
    return a + (b - a) * i


def range2d(range_x, range_y):
    """
    Creates a 2D range as a list of tuples representing all combinations of the given ranges.

    Args:
        range_x (iterable): The range of x-values.
        range_y (iterable): The range of y-values.

    Returns:
        list of tuple: A list of (x, y) tuples representing the 2D range.
    """
    range_x = list(range_x)  # Convert range_x to a list
    return [(x, y) for y in range_y for x in range_x]  # Generate all (x, y) pairs


def xrange2d(range_x, range_y):
    """
    Iterates over a 2D range, yielding each combination of the given ranges.

    Args:
        range_x (iterable): The range of x-values.
        range_y (iterable): The range of y-values.

    Yields:
        tuple: The next (x, y) tuple in the 2D range.
    """
    range_x = list(range_x)  # Convert range_x to a list
    for y in range_y:
        for x in range_x:
            yield (x, y)  # Yield each (x, y) pair


def saturate(value, low, high):
    """
    Clamps a value between a specified lower and upper bound.

    Args:
        value (float or int): The value to clamp.
        low (float or int): The lower bound.
        high (float or int): The upper bound.

    Returns:
        float or int: The clamped value.
    """
    return min(max(value, low), high)


def is_power_of_2(n):
    """
    Determines if a given number is a power of 2.

    Args:
        n (int): The number to check.

    Returns:
        bool: True if the number is a power of 2, False otherwise.
    """
    return math.log(n, 2) % 1.0 == 0.0


def next_power_of_2(n):
    """
    Returns the smallest power of 2 that is greater than or equal to the given number.

    Args:
        n (int): The input number.

    Returns:
        int: The next power of 2 that is greater than or equal to n.
    """
    return int(2 ** math.ceil(math.log(n, 2)))

if __name__ == "__main__":
    pass
    #print list(xrange2d(xrange(3), xrange(3)))
    #print range2d(xrange(3), xrange(3))
    #print is_power_of_2(7)
    #print is_power_of_2(8)
    #print is_power_of_2(9)
    #print next_power_of_2(7)
