"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This is an original file from the repo.
We did not make any change to it in final project.
"""

__author__ = 'Nick Jarvis'

import math

def combine_arrays(arr1, arr2, weight1, weight2):
    """
    Combines two 2D arrays (grids) by applying a weighted sum of corresponding elements.

    Args:
        arr1 (list of list of float): The first 2D array.
        arr2 (list of list of float): The second 2D array.
        weight1 (float): The weight to apply to the elements of arr1.
        weight2 (float): The weight to apply to the elements of arr2.

    Returns:
        list of list of float: A new 2D array where each element is the weighted sum of 
                               the corresponding elements from arr1 and arr2.
    """
    # Initialize the result array with the same dimensions as the input arrays
    to_return = [[0 for i in xrange(len(arr1))] for j in xrange(len(arr1[0]))]
    # Iterate over each element in the arrays and calculate the weighted sum
    for y in xrange(len(arr1)):
        for x in xrange(len(arr1[0])):
            to_return[x][y] = arr1[x][y] * weight1 + arr2[x][y] * weight2

    return to_return

def clamp(val, low=0, high=255):
    """
    Clamps a value within a specified range.

    Args:
        val (float or int): The value to clamp.
        low (float or int, optional): The lower bound of the range. Defaults to 0.
        high (float or int, optional): The upper bound of the range. Defaults to 255.

    Returns:
        float or int: The clamped value.
    """
    return max(min(high, val), low)

def scale_array(array, scalar):
    """
    Scales each element in a 2D array by a given scalar.

    Args:
        array (list of list of float): The 2D array to scale.
        scalar (float): The scalar value to multiply each element by.

    Returns:
        list of list of float: The scaled 2D array.
    """
    to_return = array
    # Iterate over each element in the array and multiply it by the scalar
    for y in xrange(len(array)):
        for x in xrange(len(array[0])):
            to_return[x][y] = array[x][y] * scalar

    return to_return

def pertubate(base_array, pert_array):
    """
    Perturbates a base array using a perturbation array, creating a new array with elements offset
    based on the perturbation values. The amount of offset is determined by the magnitude of the perturbation.

    Args:
        base_array (list of list of float): The base 2D array to be perturbed.
        pert_array (list of list of float): The perturbation 2D array providing the offset values.

    Returns:
        list of list of float: The perturbed 2D array.
    """
    # Initialize the result array with the same dimensions as the input arrays
    to_return = [[0 for y in xrange(len(base_array))] for x in xrange(len(base_array[0]))]

    # Determine the size and magnitude of the perturbation
    size = len(base_array) - 1
    magnitude = math.log(size + 1, 2) * ((size + 1) / 256)

    # Iterate over each element in the base array to apply the perturbation
    for y in xrange(len(base_array)):
        for x in xrange(len(base_array[0])):
            # Calculate the offset based on the perturbation array
            offset = int(((pert_array[x][y] - 128) / 128.0) * magnitude)
            # Apply the offset and clamp the result within bounds
            to_return[x][y] = clamp(base_array[clamp(x + offset, high=size)][clamp(y + offset, high=size)], 0, 255)

    return to_return

