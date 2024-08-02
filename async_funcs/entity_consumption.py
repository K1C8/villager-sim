import asyncio

from GameEntity import GameEntity
from World import DAY_DURATION

VILLAGER_FOOD_CONSUMPTION_RATE = 5
PLANT_WATER_CONSUMPTION_RATE = 2


async def consume_func_villager(entity: GameEntity):
    while True:
        await asyncio.sleep(DAY_DURATION)
        if entity.food > VILLAGER_FOOD_CONSUMPTION_RATE:
            entity.food -= VILLAGER_FOOD_CONSUMPTION_RATE
        else:
            entity.death()
            return


async def consume_func_plant(entity: GameEntity):
    while True:
        await asyncio.sleep(DAY_DURATION)
        if entity.water > 2:
            entity.water -= 2
        else:
            entity.death()

