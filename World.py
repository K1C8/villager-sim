import copy
import sys
import pygame

import Buildings
from GameEntity import GameEntity
from gametools import vector2, VoronoiMapGen, MidpointDisplacement, PertTools
from configuration.world_configuration import DAYTIME_DURATION, NIGHTTIME_DURATION, DAY_DURATION
import math
import Tile
import Clips
import Farmer
import Lumberjack
import Angler
import Explorer
import Arborist


class World(object):
    """This class holds everything in the game. It also
    updates and renders it all each frame."""

    def __init__(self, tile_dimensions, screen_size):
        """Basic initialization.

        Args:
            tile_dimensions: The dimensions of the world in terms
                of tiles. default is 128x128 tiles.

            screen_size: The size of the window, this is used for scaling
                (mostly of the minimap).

        Returns:
            None
        """

        self.tile_size = 32
        self.w, self.h = self.world_size = (tile_dimensions[0] * self.tile_size, tile_dimensions[1] * self.tile_size)
        self.world_position = vector2.Vector2(-self.w / 2, -self.h / 2)

        self.clock = pygame.time.Clock()

        self.MAXpopulation = 100
        self.MAXFish = 1000
        self.MAXCrop = 1000
        self.MAXWood = 1000
        self.MAXStone = 1000

        # Starting resources of new game
        self.wood = 100
        self.fish = 100
        self.crop = 500
        self.stone = 0

        # Time
        self.day = 0
        self.time = 0.0

        self.is_day = True
        # self.DAYTIME_DURATION = 38.0
        # self.NIGHTTIME_DURATION = 22.0
        # self.DAY_DURATION = DAYTIME_DURATION + NIGHTTIME_DURATION

        self.village_location = vector2.Vector2(self.w / 2, self.h / 2)

        # Entities
        self.entities = {}
        self.buildings = {}
        self.entity_id = 0
        self.building_id = 0

        self.farmer_count = 0
        self.lumberjack_count = 0
        self.angler_count = 0
        self.explorer_count = 0
        self.arborist_count = 0

        self.lumber_yard = []
        self.barn = []
        self.stonework = []
        self.fish_market = []
        self.rest_places = []

        self.fields = []
        self.tile_array = [[Tile.Tile]]
        self.known_fishing_spots = []

        # If a new world have no places suitable to start, then create the world again until it has one.
        has_found_starting_point = False
        while not has_found_starting_point:
            self.new_world(tile_dimensions)
            starting_point = self.find_starting_point()
            if starting_point is not None:
                has_found_starting_point = True
                self.village_location = vector2.Vector2(starting_point.x * 32, starting_point.y * 32)
                self.village_location_tile = copy.deepcopy(starting_point)

        self.populate()
        self.clipper = Clips.Clips(self, screen_size)

    def new_world(self, array_size):
        """Creates a new world (including all entities)

        Args:
            array_size: The size of the tile array, same as tile_dimensions
                in the constructor.

        Returns:
            None
        """

        map_width, map_height = array_size
        map_generator = VoronoiMapGen.mapGen()

        # midpoint_generator = MidpointDisplacement.MidpointDisplacement()
        # mid_map = PertTools.scale_array(midpoint_generator.normalize(midpoint_generator.NewMidDis(int(math.log(map_width, 2)))), 255)
        # vor_map = map_generator.whole_new_updated(size=array_size, ppr=2, c1=-1, c2=1, c3=0)

        # combined_map = PertTools.combine_arrays(vor_map, mid_map, 0.33, 0.66)

        # pert_map = PertTools.scale_array(midpoint_generator.normalize(midpoint_generator.NewMidDis(int(math.log(map_width, 2)))), 255)
        # vor_map = map_generator.radial_drop(PertTools.pertubate(combined_map, pert_map), 1.5, 0.0)
        # vor_map = map_generator.radial_drop(mid_map, 1.5, 0.0)

        vor_map = map_generator.radial_drop(map_generator.negative(map_generator.reallyCoolFull(array_size, num_p=23)),
                                            max_scalar=1.5, min_scalar=0.0)

        # All grass map for testing
        # vor_map = [[150 for x in range(128)] for y in range(128) ]

        # Method without radial drop
        # vor_map = map_generator.negative(map_generator.reallyCoolFull(array_size, num_p=23))

        self.minimap_img = pygame.Surface((map_width, map_height))
        self.tile_array = [[0 for tile_x in range(map_width)] for tile_y in range(map_height)]
        self.world_surface = pygame.Surface(self.world_size, pygame.HWSURFACE)

        do_hard_shadow = True
        shadow_height = 255
        shadow_drop = 3
        for tile_x in range(map_width):

            for tile_y in range(map_height):

                color = vor_map[tile_x][tile_y]

                if do_hard_shadow:
                    shaded = False
                    if color < shadow_height and not shadow_height < 110:
                        shaded = True
                        shadow_height -= shadow_drop

                    elif color >= 110 and color > shadow_height:
                        shadow_height = color
                        shadow_height -= shadow_drop

                    else:
                        shadow_height -= shadow_drop

                if color < 110:
                    # Water tile
                    new_tile = Tile.WaterTile(self, "AndrewWater")

                elif 120 > color >= 110:
                    # Sand / Beach tile
                    new_tile = Tile.BeachTile(self, "Sand")

                # TODO: Implement a humidity / temperature system
                elif 160 > color >= 120:
                    # Grass
                    new_tile = Tile.GrassTile(self, "MinecraftGrass")

                elif 170 > color >= 160:
                    # Tree
                    new_tile = Tile.TreePlantedTile(self, "GrassWithCenterTree")

                elif 190 > color >= 170:
                    # Grass (again)
                    new_tile = Tile.GrassTile(self, "MinecraftGrass")

                elif 220 > color >= 190:
                    # Rock
                    new_tile = Tile.SmoothStoneTile(self, "AndrewSmoothStone")

                else:
                    # Snow
                    new_tile = Tile.SnowTile(self, "MinecraftSnow")

                new_tile.location = vector2.Vector2(tile_x * self.tile_size, tile_y * self.tile_size)

                new_tile.rect.topleft = new_tile.location
                new_tile.color = color

                alph = 220 - color
                if 220 > color >= 190:
                    alph = 330 - color
                new_tile.darkness = alph

                subtle_shadow = pygame.Surface((self.tile_size, self.tile_size))
                subtle_shadow.set_alpha(alph)

                if do_hard_shadow:
                    hard_shadow = pygame.Surface((self.tile_size, self.tile_size))
                    hard_shadow.set_alpha(128)
                    if shaded:
                        new_tile.img.blit(hard_shadow, (0, 0))

                self.world_surface.blit(new_tile.img, new_tile.location)
                self.world_surface.blit(subtle_shadow, new_tile.location)

                self.minimap_img.blit(
                    new_tile.img.subsurface(
                        (0, 0, 1, 1)), (tile_x, tile_y))

                self.minimap_img.blit(
                    subtle_shadow.subsurface(
                        (0, 0, 1, 1)), (tile_x, tile_y))

                self.tile_array[tile_y][tile_x] = new_tile

    def find_starting_point(self):
        # Calculate 8x8 block count in width
        w_block_count = int(self.w / 32 // 8)
        # Calculate 8x8 block count in height
        h_block_count = int(self.h / 32 // 8)
        print("W block count: " + str(w_block_count) + " , H block count: " + str(h_block_count))
        # List of all suitable blocks to start. These tiles at least can allocate 6 buildings
        suitable_starting_blocks = []
        # List of all best blocks to start. These tiles at least can allocate 6 buildings and have ample neighboring
        # GrassTiles or TreePlantedTiles
        best_starting_blocks = []
        # Matrix to store GrassTiles and TreePlantedTiles in each block
        arable_tiles_matrix = [[0 for w in range(0, w_block_count)] for h in range(0, h_block_count)]
        # Skipping all 8x8 blocks on the edges of the map
        for block_h_coordinate in range(1, h_block_count):
            for block_w_coordinate in range(1, w_block_count):
                # There are some twists in the logic. Vector2 uses (x, y) coordinate; while tile_array uses [y][x]
                block_upperleft_tile = vector2.Vector2(block_h_coordinate * 8, block_w_coordinate * 8)
                arable_tiles = 0
                buildable_lots = 0

                # Calculate arable_tiles and buildable_lots
                for y in range(0, 8):
                    for x in range(0, 8):
                        tile = self.tile_array[block_w_coordinate * 8 + x][block_h_coordinate * 8 + y]
                        if (isinstance(tile, Tile.GrassTile) or isinstance(tile, Tile.TreePlantedTile)
                                or isinstance(tile, Tile.Baby_Tree)):
                            arable_tiles += 1
                        if y % 2 == 0 and x % 2 == 0:
                            lot_tiles = [self.tile_array[block_w_coordinate * 8 + x][block_h_coordinate * 8 + y],
                                         self.tile_array[block_w_coordinate * 8 + x + 1][block_h_coordinate * 8 + y],
                                         self.tile_array[block_w_coordinate * 8 + x][block_h_coordinate * 8 + y + 1],
                                         self.tile_array[block_w_coordinate * 8 + x +1][block_h_coordinate * 8 + y +1]]
                            lot_buildable = True
                            for tile in lot_tiles:
                                if not tile.buildable:
                                    lot_buildable = False
                            if lot_buildable:
                                buildable_lots += 1
                if buildable_lots > 5:
                    suitable_starting_blocks.append(block_upperleft_tile)
                arable_tiles_matrix[block_w_coordinate][block_h_coordinate] = arable_tiles
        print(suitable_starting_blocks)
        print(arable_tiles_matrix)
        # Calculate arable tiles sum of neighboring blocks of each block
        for starting_block in suitable_starting_blocks:
            w_block = int(starting_block.x) // 8
            h_block = int(starting_block.y) // 8
            if w_block is not None and h_block is not None and 0 < w_block < (w_block_count - 1) and 0 < h_block < (
                    h_block_count - 1):
                surround_arable_tiles = (arable_tiles_matrix[w_block - 1][h_block - 1] +
                                         arable_tiles_matrix[w_block][h_block - 1] +
                                         arable_tiles_matrix[w_block + 1][h_block - 1] +
                                         arable_tiles_matrix[w_block - 1][h_block] +
                                         arable_tiles_matrix[w_block + 1][h_block] +
                                         arable_tiles_matrix[w_block - 1][h_block + 1] +
                                         arable_tiles_matrix[w_block][h_block + 1] +
                                         arable_tiles_matrix[w_block + 1][h_block + 1])
                print("Checking block w_block: " + str(w_block) + ", h_block: " + str(h_block) + ", surrounding " +
                      "arable tiles count is: " + str(surround_arable_tiles))
                if surround_arable_tiles > 160:
                    best_starting_blocks.append(starting_block)
        print(best_starting_blocks)
        print(best_starting_blocks[len(best_starting_blocks) // 2])
        return best_starting_blocks[len(best_starting_blocks) // 2]

    def populate(self):
        """Populates the world with entities.

        Currently just does a hard-coded a specific number of
        lumberjacks and farmers in the same position.

        Args:
            None

        Returns:
            None"""

        start = {"Lumberjack": {"count": 2,
                                "state": "Searching",
                                "class": Lumberjack.Lumberjack},

                 "Angler": {"count": 1,
                            "state": "Searching",
                            "class": Angler.Angler},

                 "Arborist": {"count": 1,
                              "state": "Planting",
                              "class": Arborist.Arborist},

                 "Farmer": {"count": 0,
                            "state": "Searching",
                            "class": Farmer.Farmer},

                 "Explorer": {"count": 1,
                              "state": "Exploring",
                              "class": Explorer.Explorer}
                 }

        start_buildings = {"TownCenter": {"count": 1,
                                          "class": Buildings.TownCenter
                                          },
                           "Barn": {"count": 0,
                                    "class": Buildings.Barn
                                    },
                           "LumberYard": {"count": 0,
                                          "class": Buildings.LumberYard
                                          },
                           "Stonework": {"count": 0,
                                         "class": Buildings.Stonework
                                         },
                           "FishMarket": {"count": 0,
                                          "class": Buildings.FishMarket
                                          }
                           }

        for key in start.keys():
            for count in range(start[key]["count"]):
                new_ent = start[key]["class"](self, key)
                new_ent.location = copy.deepcopy(self.village_location)
                new_ent.brain.set_state(start[key]["state"])
                self.add_entity(new_ent)

        for key in start_buildings.keys():
            for count in range(start_buildings[key]["count"]):
                # new_building initial function call
                new_bldg_pos = self.get_next_building_pos(self.village_location_tile)
                if new_bldg_pos is not None:
                    new_bldg = None
                    location = copy.deepcopy(new_bldg_pos)
                    new_bldg = start_buildings[key]["class"](self, location, key)
                    self.add_building(new_bldg)
                    # if key == "TownCenter":
                    #     new_bldg = start_buildings[key]["class"](self, location, key)
                    #     self.add_building(new_bldg)
                    # # temporary codes
                    # elif key == "LumberYard":
                    #
                    # elif key == "Barn":
                    #
                    # elif key == "StoneStorage":


    def add_entity(self, entity):
        """Maps the input entity to the entity hash table (dictionary)
        using the entity_id variable, then increments entity_id.

        Args:
            entity: A GameEntity that will be added to the world

        Returns:
            None
        """

        self.entities[self.entity_id] = entity
        entity.id = self.entity_id
        self.entity_id += 1

        if isinstance(entity, Farmer.Farmer):
            self.farmer_count += 1
        elif isinstance(entity, Lumberjack.Lumberjack):
            self.lumberjack_count += 1
        elif isinstance(entity, Angler.Angler):
            self.angler_count += 1
        elif isinstance(entity, Explorer.Explorer):
            self.explorer_count += 1
        elif isinstance(entity, Arborist.Arborist):
            self.arborist_count += 1

    def add_building(self, building):
        self.buildings[self.building_id] = building
        building.id = self.building_id
        self.building_id += 1
        print("Building width: " + str(building.location.x))
        print("Building height: " + str(building.location.y))

        for tile_x in range(building.image.get_width() // self.tile_size):
            for tile_y in range(building.image.get_height() // self.tile_size):
                self.tile_array[int(building.location.y) + tile_y][int(building.location.x) + tile_x] = (
                    Tile.BuildingTile(self, "MinecraftGrass"))
        self.world_surface.blit(building.image, building.location * self.tile_size)

        if building is not None:
            if building.can_drop_wood:
                self.lumber_yard.append(building.location * self.tile_size)
            if building.can_drop_crop:
                self.barn.append(building.location * self.tile_size)
            if building.can_drop_fish:
                self.fish_market.append(building.location * self.tile_size)
            if building.can_drop_stone:
                self.stonework.append(building.location * self.tile_size)
            if building.supports > 0:
                self.rest_places.append(building.location * self.tile_size)

    def process(self, delta):
        """Runs through each entity and runs their process function.

        Args:
            delta: Time passed since the last frame (in seconds)

        Returns:
            None
        """

        # time increment and day/night cycle
        self.time += delta
        # if self.is_day and self.time > self.DAYTIME_DURATION:
        if self.is_day and self.time > DAYTIME_DURATION:
            self.is_day = False
        # elif not self.is_day and self.time > self.DAY_DURATION:
        elif not self.is_day and self.time > DAY_DURATION:
            # self.time = self.time - self.DAY_DURATION
            self.time = self.time - DAY_DURATION
            self.is_day = True
            self.day += 1
            for entity in self.entities.values():
                if entity is not None:
                    entity.consume_func(entity)

        for entity in self.entities.values():
            if entity is not None:
                entity.process(delta)

        # entity creation logics
        # Populate if there are enough of food for every one
        # print("Number of entities: ", len(self.entities))
        if ((self.crop + self.fish) / len(self.entities)) >= 100 and (self.crop >= 100) and (self.fish >= 100):
            # Currenltly hardcoding farmer creation
            farmer = Farmer.Farmer(self, "Farmer")
            farmer.location = copy.deepcopy(self.village_location)
            farmer.brain.set_state(farmer.primary_state)

            self.add_entity(farmer)
            self.crop -= 100
            self.fish -= 100
            print("Farmer created")

    def render(self, surface):
        """Blits the world_surface and all entities onto surface.

        Args:
            surface: The surface on which to blit everything

        Returns:
            None
        """

        surface.blit(self.world_surface, self.world_position)

        for entity in self.entities.values():
            entity.render(surface)
            if entity.active_info:
                entity.render_info_bar(surface, entity)

    def render_all(self, surface):
        """Calls the clipper's render function, which also calls
        this class's render function. Used so the main file doesn't
        have to call the clipper.

        Args:
            surface: The Pygame.Surface on which to blit everything.

            delta: The time passed (in seconds) since the last frame.

            mouse_pos: tuple of length 2 containing the position of the mouse.

        Returns:
            None
        """
        self.clipper.render(surface)

    def check_minimap_update(self, mouse_pos):
        """This code moves the view to where the user is clicking in
        the minimap. Don't ask me how it works, I have no idea.

        Args:
            mouse_pos: Vector2 instance that contains the position of the mouse

        Returns:
            None
        """

        if (mouse_pos.x > self.clipper.minimap_rect.x and
                mouse_pos.y > self.clipper.minimap_rect.y):
            x_temp_1 = -self.clipper.a * (mouse_pos.x - self.clipper.minimap_rect.x)
            x_temp_2 = self.clipper.rect_view_w * self.clipper.a
            self.world_position.x = x_temp_1 + (x_temp_2 / 2)

            y_temp_1 = -self.clipper.b * (mouse_pos.y - self.clipper.minimap_rect.y)
            y_temp_2 = self.clipper.rect_view_h * self.clipper.b
            self.world_position.y = y_temp_1 + (y_temp_2 / 2)

    def get_food_court(self, entity : GameEntity):
        food_court_candidates = []
        if len(self.barn) == 0 and len(self.fish_market) == 0:
            return None
        if self.fish > 0:
            for market in self.fish_market:
                food_court_candidates.append((market, market.get_distance_to(p=entity.location)))
        elif self.crop > 0:
            for barn in self.barn:
                food_court_candidates.append((barn, barn.get_distance_to(p=entity.location)))
        food_court_candidates = sorted(food_court_candidates, key=lambda fc: fc[1])
        if len(food_court_candidates) > 0:
            return food_court_candidates[0][0]
        # if len(self.barn) > 0:
        #     return self.barn[0]
        # elif len(self.fish_market) > 0:
        #     return self.fish_market[0]

    def get_barn(self, entity):
        if len(self.barn) > 0:
            return self.barn[0]

    def get_stonework(self, entity):
        if len(self.stonework) > 0:
            return self.stonework[0]

    def get_lumber_yard(self, entity):
        if len(self.lumber_yard) > 0:
            return self.lumber_yard[0]

    def get_fish_market(self, entity):
        if len(self.fish_market) > 0:
            return self.fish_market[0]

    def get_next_building_pos(self, grid_upperleft_tile: vector2.Vector2):
        upperleft_x = int(grid_upperleft_tile.x)
        upperleft_y = int(grid_upperleft_tile.y)
        for y in range(0, 8):
            for x in range(0, 8):
                if y % 2 == 0 and x % 2 == 0:
                    lot_tiles = [self.tile_array[upperleft_y + y][upperleft_x + x],
                                 self.tile_array[upperleft_y + y + 1][upperleft_x + x],
                                 self.tile_array[upperleft_y + y][upperleft_x + x + 1],
                                 self.tile_array[upperleft_y + y + 1][upperleft_x + x + 1]]
                    lot_buildable = True
                    for tile in lot_tiles:
                        if not tile.buildable:
                            lot_buildable = False
                    if lot_buildable:
                        return vector2.Vector2(upperleft_x + x, upperleft_y + y)
        print("No suitable lot found in given grid (" + str(upperleft_x) + ", " + str(upperleft_y) + ").")
        return None

    def delete_entity(self, entity_to_delete: GameEntity):
        """
        This function act as the function to delete entity from the world.
        Input:
            entity: The entity that is needed to be deleted, like the result of a death event.

        """
        for entity in self.entities.values():
            if entity is not None and entity == entity_to_delete:
                # Debugging use only.
                print("Entity:" + str(entity.id) + " has dead.")
                self.entities[entity_to_delete.id] = None

        del entity_to_delete
