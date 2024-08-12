"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines class for the world in game.
"""

import copy
import queue
from random import random
import pygame
import Buildings
from GameEntity import GameEntity
from aitools.BuildingDecision import building_decision
from gametools import vector2, VoronoiMapGen, MidpointDisplacement, PertTools
from configuration.world_configuration import DAYTIME_DURATION, NIGHTTIME_DURATION, DAY_DURATION, UTILIZE_LIMIT, DEBUG
import math
import Tile
import Clips
import Farmer
import Builder
import Lumberjack
import Angler
import Explorer
import Arborist
from PathFinding import create_graph


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

        self.MAXpopulation = 8
        self.MAXFish = 500
        self.MAXCrop = 500
        self.MAXWood = 500
        self.MAXStone = 500

        # Starting resources of new game
        self.wood = 100
        self.fish = 100
        self.crop = 500
        self.stone = 700

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

        self.living_entities_count = 0
        self.farmer_count = 0
        self.lumberjack_count = 0
        self.angler_count = 0
        self.explorer_count = 0
        self.arborist_count = 0
        self.builder_count = 0

        self.lumber_yard = []
        self.barn = []
        self.stonework = []
        self.fish_market = []
        self.rest_places = []

        # Related lists for farming works.
        self.fields = []
        self.sow_queue = queue.Queue()
        self.water_queue = queue.Queue()
        self.harvest_queue = queue.Queue()

        # List for builders.
        self.building_list = []
        self.unfinished_buildings = []

        self.fields_waiting_to_sow = []
        self.fields_waiting_to_water = []
        self.fields_waiting_to_harvest = []

        self.known_fishing_spots = []
        self.tile_array = [[Tile.Tile]]

        # If a new world have no places suitable to start, then create the world again until it has one.
        has_found_starting_point = False
        while not has_found_starting_point:
            self.new_world(tile_dimensions)
            starting_point = self.find_starting_point()
            if starting_point is not None:
                has_found_starting_point = True
                self.village_location = vector2.Vector2(starting_point.x * 32, starting_point.y * 32)
                self.village_location_tile = copy.deepcopy(starting_point)
        self.graph = create_graph(self)

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
        vor_map = map_generator.radial_drop(map_generator.negative(map_generator.reallyCoolFull(array_size, num_p=23)),
                                            max_scalar=1.5, min_scalar=0.0)

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
        """Find a suitable starting point for the village.

        Returns:
            Vector2: The tile position of the starting point.
        """
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
        # Matrix to store WaterTile in each block
        water_tiles_matrix = [[0 for w in range(0, w_block_count)] for h in range(0, h_block_count)]
        # Skipping all 8x8 blocks on the edges of the map
        for block_h_coordinate in range(0, h_block_count):
            for block_w_coordinate in range(0, w_block_count):
                # There are some twists in the logic. Vector2 uses (x, y) coordinate; while tile_array uses [y][x]
                block_upperleft_tile = vector2.Vector2(block_h_coordinate * 8, block_w_coordinate * 8)
                arable_tiles = 0
                water_tiles = 0
                buildable_lots = 0

                # Calculate arable_tiles and buildable_lots
                for y in range(0, 8):
                    for x in range(0, 8):
                        tile = self.tile_array[block_w_coordinate * 8 + x][block_h_coordinate * 8 + y]
                        if (isinstance(tile, Tile.GrassTile) or isinstance(tile, Tile.TreePlantedTile)
                                or isinstance(tile, Tile.Baby_Tree)):
                            arable_tiles += 1
                        if isinstance(tile, Tile.WaterTile):
                            water_tiles += 1
                        if y % 2 == 0 and x % 2 == 0:
                            lot_tiles = [self.tile_array[block_w_coordinate * 8 + x][block_h_coordinate * 8 + y],
                                         self.tile_array[block_w_coordinate * 8 + x + 1][block_h_coordinate * 8 + y],
                                         self.tile_array[block_w_coordinate * 8 + x][block_h_coordinate * 8 + y + 1],
                                         self.tile_array[block_w_coordinate * 8 + x + 1][
                                             block_h_coordinate * 8 + y + 1]]
                            lot_buildable = True
                            for tile in lot_tiles:
                                if not tile.buildable:
                                    lot_buildable = False
                            if lot_buildable:
                                buildable_lots += 1
                if buildable_lots > 5:
                    suitable_starting_blocks.append(block_upperleft_tile)
                arable_tiles_matrix[block_w_coordinate][block_h_coordinate] = arable_tiles
                water_tiles_matrix[block_w_coordinate][block_h_coordinate] = water_tiles
        print(suitable_starting_blocks)
        print(arable_tiles_matrix)
        print(water_tiles_matrix)
        # Calculate arable tiles and water tiles sum of neighboring blocks of each block
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
                surround_water_tiles = (water_tiles_matrix[w_block - 1][h_block - 1] +
                                        water_tiles_matrix[w_block][h_block - 1] +
                                        water_tiles_matrix[w_block + 1][h_block - 1] +
                                        water_tiles_matrix[w_block - 1][h_block] +
                                        water_tiles_matrix[w_block + 1][h_block] +
                                        water_tiles_matrix[w_block - 1][h_block + 1] +
                                        water_tiles_matrix[w_block][h_block + 1] +
                                        water_tiles_matrix[w_block + 1][h_block + 1])
                print("Checking block w_block: " + str(w_block) + ", h_block: " + str(h_block) + ", surrounding " +
                      "arable tiles count is: " + str(surround_arable_tiles) + ", water tiles count is " +
                      str(surround_water_tiles))
                if surround_arable_tiles > 160 and surround_water_tiles > 16:
                    best_starting_blocks.append(starting_block)
        print(best_starting_blocks)
        if len(best_starting_blocks) > 0:
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

                 "Farmer": {"count": 1,
                            "state": "Searching",
                            "class": Farmer.Farmer},

                 "Explorer": {"count": 1,
                              "state": "SearchStone",
                              "class": Explorer.Explorer},
                 "Builder": {"count": 1,
                             "state": "Waiting",
                             "class": Builder.Builder}
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

        for key in start_buildings.keys():
            for count in range(start_buildings[key]["count"]):
                # new_building initial function call
                new_bldg_pos = self.get_next_building_pos(self.village_location_tile,
                                                          start_buildings[key]["class"].SIZE_X,
                                                          start_buildings[key]["class"].SIZE_Y)
                if new_bldg_pos is not None:
                    new_bldg = None
                    location = copy.deepcopy(new_bldg_pos)
                    new_bldg = start_buildings[key]["class"](self, location, key)
                    self.add_building(new_bldg)

        for key in start.keys():
            for count in range(start[key]["count"]):
                new_ent = start[key]["class"](self, key)
                new_ent.location = copy.deepcopy(self.rest_places[0])
                new_ent.brain.set_state(start[key]["state"])
                self.add_entity(new_ent)

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
        self.living_entities_count += 1

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
        elif isinstance(entity, Builder.Builder):
            self.builder_count += 1

    def add_building(self, building):
        """Add a building to the world.

        Args:
            building (Building): The building to add.

        Returns:
            None
        """
        self.buildings[self.building_id] = building
        building.id = self.building_id
        self.building_id += 1
        print("Building x: " + str(building.location.x))
        print("Building y: " + str(building.location.y))

        for tile_x in range(building.image.get_width() // self.tile_size):
            for tile_y in range(building.image.get_height() // self.tile_size):
                # self.tile_array[int(building.location.y) + tile_y][int(building.location.x) + tile_x] = (
                #     Tile.BuildingTile(self, "MinecraftGrass"))
                new_bldg_tile = Tile.BuildingTile(self, "Cobble")
                new_bldg_tile.location = vector2.Vector2(int(building.location.x) + tile_x,
                                                         int(building.location.y) + tile_y) * 32
                new_bldg_tile.rect.topleft = new_bldg_tile.location
                self.tile_array[int(building.location.y) + tile_y][int(building.location.x) + tile_x] = new_bldg_tile
                self.world_surface.blit(new_bldg_tile.img, new_bldg_tile.location)
        self.world_surface.blit(building.image, building.location * self.tile_size)

        if building is not None:
            # All gathering point deviates one tile by one tile to the upper left corner of the building.
            if building.can_drop_wood:
                self.lumber_yard.append(building.location * self.tile_size +
                                        vector2.Vector2(self.tile_size, self.tile_size))
            if building.can_drop_crop:
                self.barn.append(building.location * self.tile_size +
                                 vector2.Vector2(self.tile_size, self.tile_size))
            if building.can_drop_fish:
                self.fish_market.append(building.location * self.tile_size +
                                        vector2.Vector2(self.tile_size, self.tile_size))
            if building.can_drop_stone:
                self.stonework.append(building.location * self.tile_size +
                                      vector2.Vector2(self.tile_size, self.tile_size))
            if building.supports > 0:
                self.rest_places.append(building.location * self.tile_size +
                                        vector2.Vector2(self.tile_size, self.tile_size))
        self.graph = create_graph(self)

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
            dice = random()
            next_class = GameEntity
            image_string = "Angler"
            if self.living_entities_count > self.MAXpopulation:
                dice = 2
            if dice < 1:
                if dice < 0.35:
                    next_class, image_string = (Angler.Angler, "Angler")
                elif dice < 0.53:
                    next_class, image_string = (Farmer.Farmer, "Farmer")
                elif dice < 0.67:
                    next_class, image_string = (Explorer.Explorer, "Explorer")
                elif dice < 0.78:
                    next_class, image_string = (Arborist.Arborist, "Arborist")
                elif dice < 0.90:
                    next_class, image_string = (Lumberjack.Lumberjack, "Lumberjack")
                else:
                    next_class, image_string = (Builder.Builder, "Builder")
                # farmer = Farmer.Farmer(self, "Farmer")
                # farmer.location = copy.deepcopy(self.village_location)
                # farmer.brain.set_state(farmer.primary_state)
                new_entity = next_class(self, image_string)
                new_entity.location = copy.deepcopy(self.rest_places[0])
                new_entity.brain.set_state(new_entity.primary_state)

                self.add_entity(new_entity)
                self.crop -= 100
                self.fish -= 100
                # print("Farmer created")
                print(image_string + " created")

        is_builder_available = False

        for entity in self.entities.values():
            if entity is not None and isinstance(entity, Builder.Builder):
                if isinstance(entity.brain.active_state, Builder.Waiting):
                    is_builder_available = True

        if is_builder_available:
            next_building = building_decision(self)
            if next_building is not None and next_building not in self.building_list:
                self.building_list.append(next_building)

        if DEBUG and len(self.building_list) > 0:
            # print("Building list length: " + str(len(self.building_list)))
            pass
        for building in self.buildings.values():
            if building is not None:
                building.update()

    def render(self, surface):
        """Blits the world_surface and all entities onto surface.

        Args:
            surface: The surface on which to blit everything

        Returns:
            None
        """

        surface.blit(self.world_surface, self.world_position)

        for entity in self.entities.values():
            if entity is not None:
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

    def get_food_court(self, entity: GameEntity):
        """Get the nearest food court for the given entity.

        Args:
            entity (GameEntity): The entity seeking food.

        Returns:
            Vector2: The location of the nearest food court.
        """
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

    def get_barn(self, entity):
        """Get the nearest barn for the given entity.

        Args:
            entity (GameEntity): The entity seeking a barn.

        Returns:
            Vector2: The location of the nearest barn.
        """
        barn_candidates = []
        if len(self.barn) > 0:
            for b in self.barn:
                barn_candidates.append((b, b.get_distance_to(entity.location)))
        barn_candidates = sorted(barn_candidates, key=lambda fm: fm[1])
        if len(barn_candidates) > 0:
            return barn_candidates[0][0]

    def get_stonework(self, entity):
        """Get the nearest stonework for the given entity.

        Args:
            entity (GameEntity): The entity seeking stonework.

        Returns:
            Vector2: The location of the nearest stonework.
        """
        stone_candidates = []
        if len(self.stonework) > 0:
            for sw in self.stonework:
                stone_candidates.append((sw, sw.get_distance_to(entity.location)))
        stone_candidates = sorted(stone_candidates, key=lambda fm: fm[1])
        if len(stone_candidates) > 0:
            return stone_candidates[0][0]

    def get_lumber_yard(self, entity):
        """Get the nearest lumber yard for the given entity.

        Args:
            entity (GameEntity): The entity seeking a lumber yard.

        Returns:
            Vector2: The location of the nearest lumber yard.
        """
        ly_candidates = []
        if len(self.lumber_yard) > 0:
            for ly in self.lumber_yard:
                ly_candidates.append((ly, ly.get_distance_to(entity.location)))
        ly_candidates = sorted(ly_candidates, key=lambda fm: fm[1])
        if len(ly_candidates) > 0:
            return ly_candidates[0][0]

    def get_fish_market(self, entity):
        """Get the nearest fish market for the given entity.

        Args:
            entity (GameEntity): The entity seeking a fish market.

        Returns:
            Vector2: The location of the nearest fish market.
        """
        fm_candidates = []
        if len(self.fish_market) > 0:
            for fm in self.fish_market:
                fm_candidates.append((fm, fm.get_distance_to(entity.location)))
        fm_candidates = sorted(fm_candidates, key=lambda fm: fm[1])
        if len(fm_candidates) > 0:
            return fm_candidates[0][0]

    def get_rest_place(self, entity):
        """Get the nearest rest place for the given entity.

        Args:
            entity (GameEntity): The entity seeking rest.

        Returns:
            Vector2: The location of the nearest rest place.
        """
        rest_candidates = []
        if len(self.rest_places) > 0:
            for rest in self.rest_places:
                rest_candidates.append((rest, rest.get_distance_to(entity.location)))
        rest_candidates = sorted(rest_candidates, key=lambda r: r[1])
        if len(rest_candidates) > 0:
            return rest_candidates[0][0]


    def get_next_building_pos(self, grid_upperleft_tile: vector2.Vector2, size_x, size_y):
        """Find the next available building position in the grid.

        Args:
            grid_upperleft_tile (Vector2): The upper-left tile of the grid.
            size_x (int): The width of the building in tiles.
            size_y (int): The height of the building in tiles.

        Returns:
            Vector2: The location of the next available building position.
        """
        upperleft_x = int(grid_upperleft_tile.x)
        upperleft_y = int(grid_upperleft_tile.y)
        for y in range(0, 8):
            for x in range(0, 8):
                if y % size_y == 0 and x % size_x == 0:
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
                self.living_entities_count -= 1
                match entity:
                    case Angler.Angler():
                        self.angler_count -= 1
                        break
                    case Arborist.Arborist():
                        self.arborist_count -= 1
                        break
                    case Builder.Builder():
                        self.builder_count -= 1
                        break
                    case Explorer.Explorer():
                        self.explorer_count -= 1
                        break
                    case Farmer.Farmer():
                        self.farmer_count -= 1
                        break
                    case Lumberjack.Lumberjack():
                        self.lumberjack_count -= 1
                        break

        del entity_to_delete
