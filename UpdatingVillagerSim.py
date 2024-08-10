"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This is the controller of villager sim.
"""

import sys
import pygame
import gametools.vector2
import TileFuncs
import World
import DebugTools
from Visualize import Visualizer
from configuration.world_configuration import LINE_COLOR, FPS

global DEBUG_MODE
DEBUG_MODE = True

def run(fullscreen, world_size=64):
    """
    The main function to run the program.

    Params:
        fullscreen: Boolean value that determines
        if the program is in fullscreen mode.

        world_size: Integer (power of 2) value that determines
        the dimensions of the game world in terms of tiles.

    Returns:
        None
    """

    pygame.init()
    
    # init font for game and debug
    pygame.font.init()
    debug_font = pygame.font.SysFont(None, 24)
    
    # set up screen
    screen_size = (1280, 720)
    if fullscreen:
        screen_size = pygame.display.list_modes()[0]
        if screen_size[0] > 1920:
            screen_size = (1920, 1080)
        screen = pygame.display.set_mode(screen_size,
                 pygame.FULLSCREEN | pygame.HWSURFACE)
    else:
        screen = pygame.display.set_mode(screen_size, 0)

    # set up world
    game_world = World.World((world_size, world_size), screen_size)
    # set up visualizer with game_world
    visualizer = Visualizer(game_world)

    # set up caption on game window
    pygame.display.set_caption("Villager Sim")

    # Tick the clock once to avoid one huge tick when the game starts
    game_world.clock.tick()

    # bool flag for pause and quit game
    pause = False
    done = False
    # tile_loc = None

    while not done:

        # Cap the game at 60 fps
        time_passed_seconds = game_world.clock.tick(FPS) / 1000.0
        pos = gametools.vector2.Vector2(*pygame.mouse.get_pos())

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:

                # debug mode 
                if event.key == pygame.K_F1:
                    global DEBUG_MODE
                    DEBUG_MODE = not DEBUG_MODE
                    
                # Escape key pressed, quit game
                if event.key == pygame.K_ESCAPE:
                    done = True

                # Space key pressed, pause game
                elif event.key == pygame.K_SPACE:
                    pause = not pause

                # F3 pressed, save screenshot
                elif event.key == pygame.K_F3:
                    pygame.image.save(game_world.world_surface, "FullScreenshot.png")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    entity = TileFuncs.get_entity(game_world, pos)
                    if entity is not None:
                        # Toggle the entity info
                        entity[1].active_info = not entity[1].active_info

                if event.button == 2:
                    pos_on_map = gametools.vector2.Vector2(pos.x - game_world.world_position.x, pos.y - game_world.world_position.y)
                    if pos_on_map.x >= 0 and pos_on_map.y >= 0:
                        tile_loc = TileFuncs.get_tile_pos(game_world, pos_on_map)
                        print("Tile clicked x:" + str(tile_loc[0]) + ", y:" + str(tile_loc[1]))


        if pygame.mouse.get_pressed()[0]:
            # check to see if the user is clicking on the minimap and update position accordingly
            game_world.check_minimap_update(pos)

        # Process everything in the game world
        if not pause:
            game_world.process(time_passed_seconds)

        # Clear the screen, then draw the world onto it
        screen.fill((0, 0, 0))
        game_world.render_all(screen)

        # Apply dark filter to screen when night time
        if not game_world.is_day:
            dark_filter = pygame.Surface(screen.get_size())
            dark_filter.fill((0, 0, 80))
            dark_filter.set_alpha(96)   # Hardcoded alpha value representing the darkness of night
            screen.blit(dark_filter, (0, 0))

        if DEBUG_MODE:
            living_entities_count = (game_world.angler_count + game_world.arborist_count + game_world.builder_count
                                     + game_world.explorer_count + game_world.farmer_count
                                     + game_world.lumberjack_count)
            # print day string to top left corner of the screen
            debug_day_string =         "Day: " + str(game_world.day)
            debug_day_status_string =  "Status: " + ("Day" if game_world.is_day else "Night")
            debug_day_time_string =    "Time: " + str(int(game_world.time))
            debug_res_wood_string =    "Wood: " + str(game_world.wood)
            debug_res_fish_string =    "Fish: " + str(game_world.fish)
            debug_res_crop_string =    "Crop: " + str(game_world.crop)
            debug_res_stone_string =   "Stone: " + str(game_world.stone)
            debug_res_entity_count =   "Entities: " + str(living_entities_count)
            debug_farmer_count =       "Farmers: " + str(game_world.farmer_count)
            debug_lumberjack_count =   "Lumberjacks: " + str(game_world.lumberjack_count)
            debug_angler_count =       "Anglers: " + str(game_world.angler_count)
            debug_explorer_count =     "Explorers: " + str(game_world.explorer_count)
            debug_arborist_count =     "Arborists: " + str(game_world.arborist_count)

            day_string_surface = debug_font.render(debug_day_string, True, (255, 255, 255)) 
            day_status_surface = debug_font.render(debug_day_status_string, True, (255, 255, 255))
            day_time_surface = debug_font.render(debug_day_time_string, True, (255, 255, 255))
            res_wood_surface = debug_font.render(debug_res_wood_string, True, (255, 255, 255))
            res_fish_surface = debug_font.render(debug_res_fish_string, True, (255, 255, 255))
            res_crop_surface = debug_font.render(debug_res_crop_string, True, (255, 255, 255))
            res_stone_surface = debug_font.render(debug_res_stone_string, True, (255, 255, 255))
            res_entity_count_surface = debug_font.render(debug_res_entity_count, True, (255, 255, 255))
            farmer_count_s = debug_font.render(debug_farmer_count, True, LINE_COLOR[5])
            lumberjack_count_s = debug_font.render(debug_lumberjack_count, True, LINE_COLOR[0])
            angler_count_s = debug_font.render(debug_angler_count, True, LINE_COLOR[1])
            explorer_count_s = debug_font.render(debug_explorer_count, True, LINE_COLOR[4])
            arborist_count_s = debug_font.render(debug_arborist_count, True, LINE_COLOR[2])

            debug_string_positions = [
                (10, 10),
                (10, 40),
                (10, 70),
                (10, 100),
                (10, 130),
                (10, 160),
                (10, 190),
                (10, 220),
                (10, 250),
                (10, 280),
                (10, 310),
                (10, 340),
                (10, 370),
            ]

            surfaces = [
                day_string_surface,
                day_status_surface,
                day_time_surface,
                res_wood_surface,
                res_fish_surface,
                res_crop_surface,
                res_stone_surface,
                res_entity_count_surface,
                farmer_count_s,
                lumberjack_count_s,
                angler_count_s,
                explorer_count_s,
                arborist_count_s,
            ]

            # Draw rectangles and blit text surfaces
            for pos, surface in zip(debug_string_positions, surfaces):
                rect = surface.get_rect(topleft=pos)
                pygame.draw.rect(screen, (0, 0, 0), rect)  # Draw black rectangle
                screen.blit(surface, pos)  # Blit text surface

            # if pos is None or tile_loc is None: continue
            # elif pos is not None and tile_loc is not None:

        # Render Visualizer
        visualizer.render(screen)
        # Update the screen
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(bool(int(sys.argv[1])))
    elif len(sys.argv) >= 3:
        run(bool(int(sys.argv[1])), int(sys.argv[2]))
    else:
        run(False, 128)
