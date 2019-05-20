from random import randint

import tcod

from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from components.item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from elements.entity import Entity
from game_messages import Message
from src.map_objects.tile import Tile
from src.map_objects.rect import Rect
from render_functions import RenderOrder


class GameMap:
    """ Game map for one screen """
    def __init__(self, width, height, room_min_size, room_max_size):
        self.width = width
        self.height = height
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.tiles = self.initialize_tiles()

        self.rooms = []

        self.number_of_bosses = 0
        self.max_number_of_bosses = 0

    def initialize_tiles(self):
        """ Fill map with impassable walls """
        tiles = [[Tile(True) for _ in range(self.height)] for _ in range(self.width)]

        return tiles

    ##
    # digging map elements
    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    ##
    # Map creation
    def make_map(self, max_rooms, player, max_monsters_per_room, max_items_per_room):
        entities = self.generate_rooms(self.width, self.height, max_rooms,
                                       max_monsters_per_room, max_items_per_room)

        # the first room is where the player starts at
        player.x, player.y = self.rooms[0].center()

        for room in self.rooms:
            self.create_room(room)

        return entities

    def generate_rooms(self, map_width, map_height, max_rooms, max_monsters_per_room, max_items_per_room):
        self.rooms = []
        entities = []
        num_rooms = 0

        for r in range(max_rooms):
            # random width and height
            w = randint(self.room_min_size, self.room_max_size)
            h = randint(self.room_min_size, self.room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)
            # run through the other rooms and see if they intersect with this one
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    break
            else:
                entities.extend(self.place_entities(new_room, max_monsters_per_room))
                entities.extend(place_items(new_room, max_items_per_room))
                self.rooms.append(new_room)

                # center coordinates of new room, will be useful later
                new_x, new_y = new_room.center()

                if num_rooms > 0:
                    # connect all rooms after the first to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = self.rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                num_rooms += 1

        return entities

    def is_blocked(self, x, y) -> bool:
        return self.tiles[x][y].blocked

    def place_entities(self, room, max_monsters_per_room):
        entities = []
        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                chance = randint(0, 100)
                if chance >= 90 and self.number_of_bosses < self.max_number_of_bosses:
                    monster = spawn_dragon(x, y)
                    self.number_of_bosses += 1
                elif chance < 80:
                    monster = spawn_orc(x, y)
                else:
                    monster = spawn_troll(x, y)

                entities.append(monster)

        return entities


def spawn_troll(x, y):
    monster = Entity(x, y, 'T', tcod.darker_green, "Troll",
                     render_order=RenderOrder.ACTOR)
    monster.set_ai(BasicMonster())
    monster.set_combat_info(Fighter(hp=16, defense=1, power=4))
    return monster


def spawn_orc(x, y):
    monster = Entity(x, y, 'o', tcod.desaturated_green, "Orc",
                     render_order=RenderOrder.ACTOR)
    monster.set_ai(BasicMonster())
    monster.set_combat_info(Fighter(hp=10, defense=0, power=3))
    return monster


def spawn_dragon(x, y):
    monster = Entity(x, y, 'D', tcod.light_flame, "Red Dragon",
                     render_order=RenderOrder.ACTOR)
    monster.set_ai(BasicMonster())
    monster.set_combat_info(Fighter(hp=20, defense=3, power=5))
    return monster


def place_items(room, max_items_per_room):
    items = []

    number_of_items = randint(0, max_items_per_room)

    for i in range(number_of_items):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)
        chance = randint(0, 100)
        if chance < 5:
            name = "Mega Healing Potion"
            color = tcod.lighter_violet
            char = '!'
            item_component = Item(use_function=heal, amount=8)
        if chance < 20:
            name = "Scroll of Confusion"
            color = tcod.light_pink
            char = '~'
            item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan))
        elif chance < 30:
            name = "Scroll of Lightning"
            color = tcod.yellow
            char = '~'
            item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
        elif chance < 60:
            name = "Scroll of Fireball"
            color = tcod.flame
            char = '~'
            item_component = Item(
                use_function=cast_fireball,
                targeting=True,
                targeting_message=Message(
                    "Left-click a target tile for the fireball, or right-click to cancel.",
                    tcod.light_cyan),
                damage=12, radius=3)
        else:
            name = "Healing Potion"
            color = tcod.violet
            char = '!'
            item_component = Item(use_function=heal, amount=4)

        if not any([entity for entity in items if entity.x == x and entity.y == y]):
            item = Entity(x, y, char, color, name, render_order=RenderOrder.ITEM)
            item.set_item(item_component)
            items.append(item)

    return items
