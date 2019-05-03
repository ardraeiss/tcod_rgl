import tcod
from map_objects.game_map import GameMap


def initialize_fov(game_map: GameMap) -> tcod.map.Map:
    fov_map = tcod.map.Map(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.walkable[y, x] = not game_map.tiles[x][y].blocked
            fov_map.transparent[y, x] = not game_map.tiles[x][y].block_sight

    return fov_map


def recompute_fov(fov_map: tcod.map.Map, x, y, radius, light_walls=True, algorithm=tcod.FOV_BASIC):
    fov_map.compute_fov(x, y, radius, light_walls, algorithm)
