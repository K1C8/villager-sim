"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This is an UNUSED file from the original repo.
"""

import pygame

pygame.init()

# Create a small screen for rendering icons
screen = pygame.display.set_mode((10, 10))

# Define colors for icon overlays
red_color = (200, 50, 50)
yellow_color = (128, 128, 0)


class new_icon_maker(object):
    """
    The new_icon_maker class is responsible for creating building icons in a game.
    It allows the creation of an icon by overlaying a tile pattern on a base image
    and can apply color filters to the icon.

    Methods:
        get_icon(big, tile, size, name): Creates a new icon by overlaying a tile pattern on the base image.
        color(big, tile, size, name, color): Applies a color overlay to the icon and saves the final image.
    """
    def __init__(self):
        pass

    def get_icon(self, big, tile, size, name):
        """
        Creates a new icon by overlaying a tile pattern on a base image.

        Args:
            big (pygame.Surface): The base image for the icon.
            tile (pygame.Surface): The tile image to be overlaid on the base image.
            size (int): The size of the tile.
            name (str): The name used to save the icon image file.

        Returns:
            pygame.Surface: The created icon as a new surface.
        """
        new_surface = pygame.Surface(big.get_size())
        x, y = big.get_size()[0]/int(size), big.get_size()[1]/int(size)
        for i in range(x):
            for a in range(y):
                new_surface.blit(tile, (i*size, a*size))

        new_surface.blit(big, (0, 0))
        pygame.image.save(new_surface, "Images/Buildings/%s_Icon.png"%name)
        return new_surface

    def color(self, big, tile, size, name, color):
        """
        Applies a color overlay to the icon and saves the final image.

        Args:
            big (pygame.Surface): The base image for the icon.
            tile (pygame.Surface): The tile image to be overlaid on the base image.
            size (int): The size of the tile.
            name (str): The name used to save the icon image file.
            color (str): The color to apply to the icon ("RED" or "SELECTED").
        """
        # Create the base icon using the get_icon method
        first_img = self.get_icon(big, tile, size, name)

        # Create a surface to apply the color overlay
        test_surface = pygame.Surface((64, 64))
        test_surface.set_alpha(128) # Set transparency level

        # Fill the overlay surface with the specified color
        if color == "RED":
            test_surface.fill(red_color)
        elif color == "SELECTED":
            test_surface.fill(yellow_color)

        # Create the final icon by combining the base icon and the color overlay
        final_icon = pygame.Surface((64, 64))
        final_icon.blit(first_img, (0, 0))
        final_icon.blit(test_surface, (0, 0))

        # Save the final icon image to the specified file path
        pygame.image.save(final_icon, "Images/Buildings/%s_%s_Icon.png"%(color, name))


maker = new_icon_maker()

big_img = pygame.image.load("Images/Buildings/TotalImage.png").convert().subsurface(64, 192, 64, 64)
big_img.set_colorkey((255, 0, 255))

tile_img = pygame.image.load("Images/Tiles/MinecraftGrass.png").convert()
icon1 = maker.get_icon(big_img, tile_img, 32, "TownHall")
