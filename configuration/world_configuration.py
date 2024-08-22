"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains all configuration constants for the world.
"""

# Configuration of day and night
DAYTIME_DURATION = 38.0
NIGHTTIME_DURATION = 22.0
DAY_DURATION = DAYTIME_DURATION + NIGHTTIME_DURATION

# Configuration of maximum managed tiles for each farmer
TILES_PER_FARMER = 20

# Size of tile
WORLD_TILE_SIZE = 32

# FPS Target
FPS = 60

# Debug flag
DEBUG = True

# Utilize upper limit for buildings
UTILIZE_LIMIT = 0.9

# Configuration for colors
LINE_COLOR = [(255, 0, 0), # Red - Lumberjack
              (255, 255, 0), # Yellow - Angler
              (255, 255, 255), # White - Arborist
              (127, 255, 255), # Light Blue - Builder
              (185, 28, 202), # Purple - Explorer
              (255, 167, 0), # Orange - Farmer
              (100, 45, 0) # Brown - FishingShip
              ]