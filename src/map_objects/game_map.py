from random import randint

from map_objects.tile import Tile
from rect import Rect


class GameMap:
    """ Game map for one screen """
    def __init__(self, width, height, room_min_size, room_max_size):
        self.width = width
        self.height = height
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

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
        rooms = self.generate_rooms(self.width, self.height, max_rooms)

        # the first room is where the player starts at
        player.x, player.y = rooms[0].center()

        for room in rooms:
            self.create_room(room)

    def generate_rooms(self, map_width, map_height, max_rooms):
        rooms = []
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
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                rooms.append(new_room)

                # center coordinates of new room, will be useful later
                new_x, new_y = new_room.center()

                if num_rooms > 0:
                    # connect all rooms after the first to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

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

        return rooms

    def is_blocked(self, x, y) -> bool:
        return self.tiles[x][y].blocked
