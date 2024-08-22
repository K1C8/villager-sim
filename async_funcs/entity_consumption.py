"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains functions related to villagers consuming food and plant growth.
When there are not enough food or water supply, villagers or plants will die. 
"""

import asyncio

from GameEntity import GameEntity
from configuration.world_configuration import DAY_DURATION

VILLAGER_FOOD_CONSUMPTION_RATE = 20
PLANT_WATER_CONSUMPTION_RATE = 1


async def sleep(duration):
    """
    Asynchronous sleep function that pauses execution for a given duration.

    Args:
        duration (float): The amount of time to sleep, typically in seconds.
    """
    await asyncio.sleep(DAY_DURATION)


def consume_func_villager(entity: GameEntity):
    """
    Function to simulate the consumption of food by a villager entity.
    This function decreases the villager's food supply and checks if the entity 
    should die if the food supply runs out.

    Args:
        entity (GameEntity): The villager entity consuming food.
    """
    # asyncio.run(sleep(DAY_DURATION))
    # print("Entity " + entity.name + " consumed food " + str(VILLAGER_FOOD_CONSUMPTION_RATE))
    entity.food -= VILLAGER_FOOD_CONSUMPTION_RATE
    if entity.food <= 0:
        entity.death()
        return


def consume_func_plant(entity: GameEntity):
    """
    Function to simulate the consumption of water by a plant entity.
    This function decreases the plant's water supply and checks if the entity 
    should die if the water supply runs out.

    Args:
        entity (GameEntity): The plant entity consuming water.
    """
    # asyncio.run(sleep(DAY_DURATION))
    entity.water -= PLANT_WATER_CONSUMPTION_RATE
    if entity.water <= 0:
        entity.death()
        return
