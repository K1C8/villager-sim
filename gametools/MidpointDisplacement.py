"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This is an original file from the repo.
We did not make any change to it in final project.
"""

import random

class MidpointDisplacement(object):
    """
    The MidpointDisplacement class generates a 2D heightmap using the midpoint displacement algorithm.
    This algorithm is used to create fractal terrain with a random, natural appearance.

    Methods:
        NewMidDis(N): Generates a new heightmap with a resolution of 2^N x 2^N using the midpoint displacement algorithm.
        rand_h(r): Returns a random height offset for the current recursion depth.
        normalize(array): Normalizes the values in the heightmap to be between 0 and 1.
        diamond(array, recursion_depth, iteration_x, iteration_y, N): Performs the diamond step in the midpoint displacement algorithm.
        square(array, recursion_depth, iteration, N): Placeholder for the square step (currently not implemented).
    """
    def NewMidDis(self, N):
        """
        Generates a new heightmap with a resolution of 2^N x 2^N using the midpoint displacement algorithm.

        Args:
            N (int): The exponent that determines the resolution of the heightmap (2^N x 2^N).

        Returns:
            list of list of float: A 2D list representing the heightmap, with values ranging from 0 to 1.
        """
        WIDTH = HEIGHT = (2 ** N) # The width and height of the heightmap
        # Initialize a 2D array with all values set to 0
        to_return = [[0 for x in xrange(WIDTH + 1)] for y in xrange(HEIGHT + 1)]

        # Set the initial corner values to random values
        to_return[0][0] = random.random()
        to_return[WIDTH][0] = random.random()
        to_return[WIDTH][HEIGHT] = random.random()
        to_return[0][HEIGHT] = random.random()

        # Perform the diamond and square steps for each level of recursion
        for r in xrange(N):
            for y in xrange(2 ** r):
                for x in xrange(2 ** r):
                    self.diamond(to_return, r, x, y, N)
            
            # print r, "iterations done"
            # print "size was", ((2 ** N) / (2 ** r))
            # print "there were", 2 ** r, "iterations in each dimension"
            # print ""

        return to_return

    def rand_h(self, r):
        """
        Returns a random height offset for the current recursion depth.

        Args:
            r (int): The current recursion depth.

        Returns:
            float: A random height offset that decreases with increasing recursion depth.
        """
        return (2 * (random.random() - 0.5)) / (2 ** (r + 1))

    def normalize(self, array):
        """
        Normalizes the values in the heightmap to be between 0 and 1.

        Args:
            array (list of list of float): The 2D list representing the heightmap.

        Returns:
            list of list of float: The normalized heightmap.
        """
        r_array = array
        
        # Find the minimum and maximum values in the heightmap
        min_val = r_array[0][0]
        max_val = r_array[0][0]

        for y in xrange(len(r_array)):
            for x in xrange(len(r_array[0])):
                min_val = min(r_array[x][y], min_val)
                max_val = max(r_array[x][y], max_val)

        # Normalize each value in the heightmap to be between 0 and 
        for y in xrange(len(r_array)):
            for x in xrange(len(r_array[0])):
                r_array[x][y] -= min_val
                r_array[x][y] /= (max_val - min_val)

        return r_array

    def diamond(self, array, recursion_depth, iteration_x, iteration_y, N):
        """
        Performs the diamond step in the midpoint displacement algorithm.
        This step calculates the midpoint value for a square of four points and sets the value in the center.

        Args:
            array (list of list of float): The 2D list representing the heightmap.
            recursion_depth (int): The current depth of recursion.
            iteration_x (int): The x-coordinate of the square in the grid.
            iteration_y (int): The y-coordinate of the square in the grid.
            N (int): The exponent that determines the resolution of the heightmap.
        """
        size = ((2 ** N) / (2 ** recursion_depth)) # Calculate the size of the current square
        tl = array[size * iteration_x][size * iteration_y] # Top-left corner
        tr = array[size * iteration_x + size][size * iteration_y] # Top-right corner
        br = array[size * iteration_x + size][size * iteration_y + size] # Bottom-right corner
        bl = array[size * iteration_x][size * iteration_y + size] # Bottom-left corner

        # Calculate the midpoint value and apply a random offset
        array[size * iteration_x + size / 2][size * iteration_y + size / 2] = ((tl + tr + br + bl) / 4) + self.rand_h(recursion_depth + 1)

        # Square step (not yet implemented, but placeholders for top, right, bottom, and left midpoints)
        mid = array[size * iteration_x + size / 2][size * iteration_y + size / 2]

        # top mid
        array[size * iteration_x + size / 2][size * iteration_y] = (tl + tr + mid) / 3 + self.rand_h(recursion_depth)

        # right mid
        array[size * iteration_x + size][size * iteration_y + size / 2] = (tr + br + mid) / 3 + self.rand_h(recursion_depth)

        # bottom mid
        array[size * iteration_x + size / 2][size * iteration_y + size] = (bl + br + mid) / 3 + self.rand_h(recursion_depth)

        # left mid
        array[size * iteration_x][size * iteration_y + size / 2] = (tl + bl + mid) / 3 + self.rand_h(recursion_depth)

    def square(self, array, recursion_depth, iteration, N):
        pass

