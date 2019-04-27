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
    def make_map(self):
        room1 = Rect(20, 15, 10, 15)
        room2 = Rect(35, 15, 10, 15)

        self.create_room(room1)
        self.create_room(room2)

        self.create_h_tunnel(25, 40, 23)

    def is_blocked(self, x, y) -> bool:
        return self.tiles[x][y].blocked
