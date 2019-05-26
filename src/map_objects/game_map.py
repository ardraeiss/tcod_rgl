from random import randint

import tcod

from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from components.item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from components.stairs import Stairs
from elements.entity import Entity
from game_messages import Message
from random_utils import random_choice_from_dict, from_dungeon_level
from src.map_objects.tile import Tile
from src.map_objects.rect import Rect
from render_functions import RenderOrder


class GameMap:
    """ Game map for one screen """
    def __init__(self, width, height, room_min_size, room_max_size, dungeon_level=1):
        self.width = width
        self.height = height
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.tiles = self.initialize_tiles()

        self.rooms = []

        self.dungeon_level = dungeon_level

        self.number_of_bosses = 0
        self.max_number_of_bosses = from_dungeon_level([[1, 3], [3, 5], [7, 7]], self.dungeon_level)

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
    def make_map(self, max_rooms, player):
        entities = self.generate_rooms(self.width, self.height, max_rooms)

        # the first room is where the player starts at
        player.x, player.y = self.rooms[0].center()

        for room in self.rooms:
            self.create_room(room)

        return entities

    def generate_rooms(self, map_width, map_height, max_rooms):
        self.rooms = []
        entities = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

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
                entities.extend(self.place_entities(new_room))
                entities.extend(self.place_items(new_room))
                self.rooms.append(new_room)

                # center coordinates of new room, will be useful later
                new_x, new_y = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms > 0:
                    # connect all rooms after the first to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = self.rooms[num_rooms - 1].center()

                    self.dig_tunnel_to_previous_room(new_x, new_y, prev_x, prev_y)

                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, render_order=RenderOrder.STAIRS)
        down_stairs.set_appearance('>', tcod.white, 'Stairs')
        down_stairs.set_stairs(stairs_component)
        entities.append(down_stairs)

        return entities

    def dig_tunnel_to_previous_room(self, new_x, new_y, prev_x, prev_y):
        # flip a coin (random number that is either 0 or 1)
        if randint(0, 1) == 1:
            # first move horizontally, then vertically
            self.create_h_tunnel(prev_x, new_x, prev_y)
            self.create_v_tunnel(prev_y, new_y, new_x)
        else:
            # first move vertically, then horizontally
            self.create_v_tunnel(prev_y, new_y, prev_x)
            self.create_h_tunnel(prev_x, new_x, new_y)

    def is_blocked(self, x, y) -> bool:
        return self.tiles[x][y].blocked

    def place_entities(self, room):
        entities = []
        # Get a random number of monsters
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        number_of_monsters = randint(0, max_monsters_per_room)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level),
            'red_dragon': from_dungeon_level([[5, 5], [10, 6], [15, 7]], self.dungeon_level),
        }

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'red_dragon' and self.number_of_bosses < self.max_number_of_bosses:
                    monster = spawn_dragon(x, y)
                    self.number_of_bosses += 1
                elif monster_choice == 'troll':
                    monster = spawn_troll(x, y)
                else:
                    monster = spawn_orc(x, y)

                entities.append(monster)

        return entities

    def place_items(self, room):
        items = []

        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        number_of_items = randint(0, max_items_per_room)

        item_chances = {
            'healing_potion': 35,
            'super_healing': from_dungeon_level([[10, 3]], self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            item_choice = random_choice_from_dict(item_chances)
            if item_choice == 'healing_potion':
                name = "Healing Potion"
                color = tcod.violet
                char = '!'
                item_component = Item(use_function=heal, amount=40)
            elif item_choice == 'super_healing':
                name = "Mega Healing Potion"
                color = tcod.lighter_violet
                char = '!'
                item_component = Item(use_function=heal, amount=80)
            elif item_choice == 'confusion_scroll':
                name = "Scroll of Confusion"
                color = tcod.light_pink
                char = '~'
                item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                    'Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan))
            elif item_choice == 'lightning_scroll':
                name = "Scroll of Lightning"
                color = tcod.yellow
                char = '~'
                item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
            elif item_choice == 'fireball_scroll':
                name = "Scroll of Fireball"
                color = tcod.flame
                char = '~'
                item_component = Item(
                    use_function=cast_fireball,
                    targeting=True,
                    targeting_message=Message(
                        "Left-click a target tile for the fireball, or right-click to cancel.",
                        tcod.light_cyan),
                    damage=25, radius=3)

            if not any([entity for entity in items if entity.x == x and entity.y == y]):
                item = Entity(x, y, render_order=RenderOrder.ITEM)
                item.set_appearance(char, color, name)
                item.set_item(item_component)
                items.append(item)

        return items

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.max_number_of_bosses = from_dungeon_level([[1, 3], [2, 5], [3, 7], [5, 8], [8, 9]], self.dungeon_level)

        self.room_min_size, self.room_max_size = constants['room_min_size'], constants['room_max_size']
        self.width, self.height = constants['map_width'], constants['map_height']

        self.tiles = self.initialize_tiles()
        entities.extend(self.make_map(constants['max_rooms'], player))

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', tcod.light_violet))

        return entities


def spawn_troll(x, y):
    monster = Entity(x, y, render_order=RenderOrder.ACTOR)
    monster.set_appearance('T', tcod.darker_green, "Troll")
    monster.set_ai(BasicMonster())
    monster.set_combat_info(Fighter(hp=30, defense=2, power=8, xp=100))
    return monster


def spawn_orc(x, y):
    monster = Entity(x, y, render_order=RenderOrder.ACTOR)
    monster.set_appearance('o', tcod.desaturated_green, "Orc")
    monster.set_ai(BasicMonster())
    monster.set_combat_info(Fighter(hp=20, defense=0, power=4, xp=35))
    return monster


def spawn_dragon(x, y):
    monster = Entity(x, y, render_order=RenderOrder.ACTOR)
    monster.set_appearance('D', tcod.light_flame, "Red Dragon")
    monster.set_ai(BasicMonster())
    monster.set_combat_info(Fighter(hp=35, defense=4, power=12, xp=300))
    return monster
