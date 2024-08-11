"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

The Ani class handles basic sprite sheet animations by cycling through animation frames.
Given the total number of frames and a counter for controlling the animation speed,
this class can return the current frame to be displayed.
"""


class Ani(object):
    """
    Creates an animation given the cell width, height, and the image and it returns the image needed at the time passed
    in seconds
    """

    def __init__(self,num,counter):
        """
        Initializes the Ani object with the total number of frames and the counter value.

        Args:
            num (int): The total number of frames in the animation.
            counter (int): The counter value that controls the speed of the animation.
        """
        self.counter_max = counter # The maximum counter value before advancing to the next frame
        self.counter = counter # The current counter value
        self.finished = False # Indicates if the animation cycle has completed
        self.ani_num_max = num # The total number of frames in the animation
        self.ani_num = 0 # The current frame number


    def reset(self):
        """
        Resets the animation to the first frame and resets the counter.
        This method is called when the animation completes a full cycle.
        """
        self.counter = self.counter_max # Reset the counter to the maximum value
        self.ani_num = 0 # Reset the frame number to the first frame


    def get_frame(self):
        """
        Advances the animation by one step and returns the current frame number.
        If the end of the animation is reached, it resets to the beginning.

        Returns:
            int: The current frame number to be displayed.
        """
        self.counter -= 1
        if self.counter <= 0: # If the counter has reached zero, advance to the next frame
            self.counter = self.counter_max # Reset the counter
            self.ani_num += 1 # Advance to the next frame
            if self.ani_num == self.ani_num_max: # If the last frame is reached
                self.reset() # Reset the animation
                self.finished = True # Mark the animation as finished
        return self.ani_num


