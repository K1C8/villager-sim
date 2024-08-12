"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This is an original file from the repo.
We did not make any change to it in final project.
"""

import pygame

# Load the images for the dial and its outline
dialol = pygame.image.load("Images/Dial/dial_outline2.png")
dial = pygame.image.load("Images/Dial/dial.png")
# Set the color key for transparency 
dialol.set_colorkey((255, 0, 255))
dial.set_colorkey((255, 0, 255))

# List of available buildings in the game
buildings = ["House", "LumberYard", "Dock", "Manor", "Town Center"]


class Clips(object):
    """
    ______________________
    |                    |
    |                    |
    |                    |
    |                    |
    |                    |
    |                    |
    |               _____|
    |              |MINI-|
    |              |MAP  |
    ----------------------
    """
    """
    This class manages the rendering of the game's minimap and dial, along with other UI elements.
    It handles the positioning, scaling, and drawing of these elements on the screen.

    The minimap is a smaller representation of the game world, showing the player's current view.
    The dial is a rotating image that could represent a timer or direction indicator.
    """
    def __init__(self, world, screen_size):
        """
        Initializes the Clips object with references to the game world and screen size.

        Args:
            world (World): The game world object that contains the minimap and other entities.
            screen_size (tuple): The size of the game screen (width, height).
        """
        self.size = screen_size
        self.world = world

        # The minimap is 1/4 the size of the screen in each dimension (1/16 total size)
        self.minimap_size = int(self.size[0] / 4), int(self.size[1] / 4)

        # TODO: Is this necessary?
        self.minimap = pygame.transform.scale(
            self.world.minimap_img,
            self.minimap_size)

        # Ratio between the size of the tile array and the minimap size
        self.a = self.world.w / float(self.minimap_size[0])
        self.b = self.world.h / float(self.minimap_size[1])

        # Not quite sure what this does
        self.rect_view_w = (self.size[0] / self.a) - ((self.size[0] / self.a) / 5)
        self.rect_view_h = self.size[1] / self.b

        self.minimap_rect = pygame.Rect(self.size[0] - self.minimap_size[0], self.size[1] - self.minimap_size[1],
                                        self.minimap_size[0], self.minimap_size[1])

    def render(self, surface):
        """
        Renders the minimap and the player's view rectangle onto the given surface.

        Args:
            surface (pygame.Surface): The surface on which to draw the minimap and view rectangle.
        """
        # Calculate the position of the view rectangle on the minimap
        rect_view_pos = (
            (-1 * self.world.world_position.x / self.a) + self.size[0] - self.minimap_size[0] + ((self.size[0] / 5) / self.a),
            (-1 * self.world.world_position.y / self.b) + self.size[1] - self.minimap_size[1])

        rect_view = (
            rect_view_pos,
            (self.rect_view_w,
             self.rect_view_h))

        self.world.render(surface)
        # self.update_dial(surface, tp)

        # Draw minimap below here ------------------
        surface.set_clip(self.minimap_rect)

        # Drawing the actual minimap
        surface.blit(self.minimap, self.minimap_rect)

        # Draw the white rectangle displaying where the user is located
        pygame.draw.rect(surface, (255, 255, 255), rect_view, 1)

        # Draw a black border
        pygame.draw.rect(surface, (0, 0, 0), self.minimap_rect, 2)

        surface.set_clip(None)
        # Draw minimap above here --------------------

    def update_dial(self, surface, tp):  # Dial goes below here
        """
        Updates and renders the rotating dial on the screen.

        Args:
            surface (pygame.Surface): The surface on which to draw the dial.
            tp (float): The time progression value to update the dial's rotation.
        """
        # Position the dial on the screen
        box = (self.size[0] - 55, self.size[1] / 50 - 40)
        boxtest = pygame.Rect((box[0] - 20, box[1] + 80), (50, 50))
        oldCenter = boxtest.center
        # Rotate the dial image based on the world's clock degree
        rotateddial = pygame.transform.rotate(dial, self.world.clock_degree)
        rotRect = rotateddial.get_rect()
        rotRect.center = oldCenter
        # Update the world's clock degree and reset if it exceeds 360 degrees
        self.world.clock_degree += tp
        if self.world.clock_degree >= 360.0:
            self.world.clock_degree = 0.0

        # Blit the rotated dial and its outline onto the surface
        surface.blit(rotateddial, rotRect)
        surface.blit(dialol, (box[0] - 44, box[1] + 55))