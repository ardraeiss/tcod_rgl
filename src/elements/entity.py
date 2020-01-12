from typing import Dict

import math
import tcod

from components.item import Item
from render_functions import RenderOrder


class Entity:
    """ A game entity: mob, item, environment element """
    def __init__(self, x, y, blocks_movement=True,
                 render_order=RenderOrder.CORPSE,
                 components: Dict = None):
        self.x = x
        self.y = y
        self.render_order = render_order
        self.blocks_movement = blocks_movement

        self.name = "NOBODY"
        self.char = None
        self.color = None
        self.fighter = None
        self.ai = None
        self.inventory = None
        self.item = None
        self.stairs = None
        self.level = None

        self.fighter = None
        self.ai = None
        self.inventory = None
        self.item = None
        self.stairs = None
        self.level = None
        self.equipment = None
        self.equippable = None

        if components:
            self.init_components(components)

    def init_components(self, components):
        for name in ('fighter', 'ai', 'inventory', 'item', 'stairs', 'level', 'equipment', 'equippable'):
            comp = components.get(name, None)
            if comp:
                self.__dict__[name] = comp
                comp.set_owner(self)

        if self.equippable and not self.item:
            item = Item()
            self.item = item
            self.item.set_owner(self)

    def set_appearance(self, char, color, name):
        self.char = char
        self.color = color
        self.name = name

    def is_alive(self):
        return self.fighter and self.fighter.hp > 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move_astar(self, target, entities: list, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = tcod.map.Map(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                fov.transparent[y1, x1] = not game_map.tiles[x1][y1].block_sight
                fov.walkable[y1, x1] = not game_map.tiles[x1][y1].blocked

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in (e for e in entities if e.blocks_movement and e != self and e != target):
            # Set the tile as a wall so it must be navigated around
            fov.transparent[entity.y, entity.x] = True
            fov.walkable[entity.y, entity.x] = False

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other
        # rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's
        # an alternative path really far away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster
            # blocks a corridor) it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

            # Delete the path to free memory
        tcod.path_delete(my_path)


def get_blocking_entities_at_location(entities, x, y):
    return next(
        (
            e for e in entities
            if e.blocks_movement and e.x == x and e.y == y
        ),
        None
    )
