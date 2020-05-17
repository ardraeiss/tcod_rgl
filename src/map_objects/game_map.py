from random import randint

import tcod

from components.equippable import Equippable
from components.item import Item
from components.item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from components.stairs import Stairs
from elements.entity import Entity
from equipment_slots import EquipmentSlots
from game_messages import Message
from random_utils import random_choice_from_dict, from_dungeon_level
from src.map_objects.tile import Tile
from src.map_objects.rect import Rect
from src import mobs
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
        self.max_number_of_bosses = from_dungeon_level(mobs.BOSSES_NUMBER_BY_DEPTH, self.dungeon_level)

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
        entities = self.generate_rooms(self.width, self.height, max_rooms, player)

        # the first room is where the player starts at
        player.x, player.y = self.rooms[0].center()

        for room in self.rooms:
            self.create_room(room)

        return entities

    def generate_rooms(self, map_width, map_height, max_rooms, player):
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
                entities.extend(self.place_entities(new_room, player))
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

        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, render_order=RenderOrder.STAIRS,
                             components={'stairs': Stairs(self.dungeon_level + 1), })
        down_stairs.set_appearance('>', tcod.white, 'Stairs')
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

    def is_blocked(self, x: int, y: int) -> bool:
        return self.tiles[x][y].blocked

    def place_entities(self, room, player):
        entities = []
        # Get a random number of monsters
        max_monsters_per_room = from_dungeon_level(mobs.MAX_MONSTERS_PER_ROOM_BY_DEPTH, self.dungeon_level)
        number_of_monsters = randint(0, max_monsters_per_room)

        monster_chances = mobs.get_monster_chances_by_depth(self.dungeon_level)

        # TODO extract monsters generation
        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]) and \
                    player.x != x and player.y != y:
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice in mobs.BOSS_MONSTERS:
                    if self.number_of_bosses < self.max_number_of_bosses:
                        self.number_of_bosses += 1
                    else:
                        monster_choice = 'kobold'

                monster = mobs.spawn_regular_monster(x, y, monster_choice)

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
            'confusion_scroll': from_dungeon_level([[4, 2]], self.dungeon_level),
            'short_sword': from_dungeon_level([[5, 2], [10, 3], [5, 5], [0, 6]], self.dungeon_level),
            'long_sword': from_dungeon_level([[5, 3], [10, 5], [5, 7], [0, 8]], self.dungeon_level),
            'mithril_sword': from_dungeon_level([[5, 6], [10, 7], [5, 9]], self.dungeon_level),
            'buckler_shield': from_dungeon_level([[15, 4], [5, 5], [0, 6]], self.dungeon_level),
            'small_shield': from_dungeon_level([[15, 6], [5, 8], [0, 9]], self.dungeon_level),
            'tower_shield': from_dungeon_level([[5, 8], [10, 10]], self.dungeon_level),
            'meteorite_shield': from_dungeon_level([[5, 9], ], self.dungeon_level),
        }

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            equippable_component = None
            item_component = None

            # TODO extract items data
            # TODO extract items generation
            item_choice = random_choice_from_dict(item_chances)
            if item_choice == 'super_healing':
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

            elif item_choice == 'short_sword':
                equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=4)
                char = ')'
                color = tcod.light_grey
                name = 'Short Sword'

            elif item_choice == 'long_sword':
                equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=5)
                char = ')'
                color = tcod.light_gray
                name = 'Long Sword'

            elif item_choice == 'mithril_sword':
                equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=7)
                char = ')'
                color = tcod.dark_sky
                name = 'Mithril Sword'

            elif item_choice == 'buckler_shield':
                equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                char = '['
                color = tcod.gray
                name = 'Buckler Shield'

            elif item_choice == 'small_shield':
                equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
                char = '['
                color = tcod.darker_orange
                name = 'Small Shield'

            elif item_choice == 'tower_shield':
                equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=4)
                char = '['
                color = tcod.desaturated_orange
                name = 'Tower Shield'

            elif item_choice == 'meteorite_shield':
                equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=6)
                char = '['
                color = tcod.dark_blue
                name = 'Meteorite Tower Shield'

            else:  # item_choice == 'healing_potion':
                name = "Healing Potion"
                color = tcod.violet
                char = '!'
                item_component = Item(use_function=heal, amount=40)

            if not any([entity for entity in items if entity.x == x and entity.y == y]):
                item = Entity(x, y, render_order=RenderOrder.ITEM, components={
                    'item': item_component,
                    'equippable': equippable_component,
                })
                item.set_appearance(char, color, name)
                items.append(item)

        return items

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.max_number_of_bosses = from_dungeon_level(mobs.BOSSES_NUMBER_BY_DEPTH, self.dungeon_level)

        self.room_min_size, self.room_max_size = constants['room_min_size'], constants['room_max_size']
        self.width, self.height = constants['map_width'], constants['map_height']

        self.tiles = self.initialize_tiles()
        entities.extend(self.make_map(constants['max_rooms'], player))

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', tcod.light_violet))

        return entities
