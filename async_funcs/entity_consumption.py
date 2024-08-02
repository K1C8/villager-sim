import asyncio

from GameEntity import GameEntity
from configuration.world_configuration import DAY_DURATION

VILLAGER_FOOD_CONSUMPTION_RATE = 20
PLANT_WATER_CONSUMPTION_RATE = 1


async def sleep(duration):
    await asyncio.sleep(DAY_DURATION)


def consume_func_villager(entity: GameEntity):
    # asyncio.run(sleep(DAY_DURATION))
    if entity.food > VILLAGER_FOOD_CONSUMPTION_RATE:
        print("Entity " + entity.name + " consumed food " + str(VILLAGER_FOOD_CONSUMPTION_RATE))
        entity.food -= VILLAGER_FOOD_CONSUMPTION_RATE
    else:
        entity.death()
        return


def consume_func_plant(entity: GameEntity):
    # asyncio.run(sleep(DAY_DURATION))
    if entity.water > 2:
        entity.water -= 2
    else:
        entity.death()



