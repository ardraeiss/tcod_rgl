from random import randint

from map_objects.tile import Tile
from rect import Rect


class GameMap:
    """ Game map for one screen """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.tiles = self.initialize_tiles()

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

    def create_h_tunnel(self, x, y, w):
        self.create_room(Rect(x-1, y-1, w+1, 3))

    def create_w_tunnel(self, x, y, h):
        self.create_room(Rect(x-1, y-1, 3, h+1))

    ##
    # Map creation
    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player):
        rooms = []

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)
            rooms.append(Rect(x, y, w, h))

        for room in rooms:
            self.create_room(room)

    def is_blocked(self, x, y) -> bool:
        return self.tiles[x][y].blocked
