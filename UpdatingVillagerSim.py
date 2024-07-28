#!python2

"""This will basically be a rewrite of the original file,
   but this time with a focus on clean code and commenting."""

import sys
import pygame
import gametools.vector2
import TileFuncs
import World
import DebugTools

global DEBUG_MODE
DEBUG_MODE = True

def run(fullscreen, world_size=64):
    """The main function to run the program.

    Args:
        fullscreen: Boolean value that determines if the program is
            in fullscreen mode.

        world_size: Integer (power of 2) value that determines the
            dimensions of the game world in terms of tiles.

    Returns:
        None
    """

    pygame.init()
    
    # init font
    pygame.font.init()
    debug_font = pygame.font.SysFont(None, 24)
    
    screen_size = (1280, 720)
    if fullscreen:
        screen_size = pygame.display.list_modes()[0]
        if screen_size[0] > 1920:
            screen_size = (1920, 1080)
        screen = pygame.display.set_mode(screen_size,
                 pygame.FULLSCREEN | pygame.HWSURFACE)
    else:
        screen = pygame.display.set_mode(screen_size, 0)

    game_world = World.World((world_size, world_size), screen_size)

    pygame.display.set_caption("Villager Sim")

    # Tick the clock once to avoid one huge tick when the game starts
    game_world.clock.tick()

    pause = False

    done = False
    while not done:

        # Cap the game at 60 fps
        time_passed_seconds = game_world.clock.tick(60) / 1000.0
        pos = gametools.vector2.Vector2(*pygame.mouse.get_pos())

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:

                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

                elif event.key == pygame.K_SPACE:
                    pause = not pause

                elif event.key == pygame.K_F3:
                    pygame.image.save(game_world.world_surface, "FullScreenshot.png")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    entity = TileFuncs.get_entity(game_world, pos)
                    if entity is not None:
                        # Toggle the entity info
                        entity[1].active_info = not entity[1].active_info

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
            dark_filter.fill((0, 0, 0))
            dark_filter.set_alpha(50) # Hardcoded alpha value representing the darkness of night
            screen.blit(dark_filter, (0, 0))

        if DEBUG_MODE:
        # print day string to top left corner of the screen
            debug_day_string =         "Day: " + str(game_world.day)
            debug_day_status_string =  "Status: " + ("Day" if game_world.is_day else "Night")
            debug_day_time_string =    "Time: " + str(int(game_world.time))
            debug_res_wood_string =    "Wood: " + str(game_world.wood)
            debug_res_fish_string =    "Fish: " + str(game_world.fish)
            
            day_string_surface = debug_font.render(debug_day_string, True, (255, 255, 255)) 
            day_status_surface = debug_font.render(debug_day_status_string, True, (255, 255, 255))
            day_time_surface = debug_font.render(debug_day_time_string, True, (255, 255, 255))
            res_wood_surface = debug_font.render(debug_res_wood_string, True, (255, 255, 255))
            res_fish_surface = debug_font.render(debug_res_fish_string, True, (255, 255, 255))

            screen.blit(day_string_surface, (10, 10))
            screen.blit(day_status_surface, (10, 40))
            screen.blit(day_time_surface, (10, 70))  
            screen.blit(res_wood_surface, (10, 100))
            screen.blit(res_fish_surface, (10, 130))

        # Update the screen
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(bool(int(sys.argv[1])))
    elif len(sys.argv) >= 3:
        run(bool(int(sys.argv[1])), int(sys.argv[2]))
    else:
        run(True, 128)
