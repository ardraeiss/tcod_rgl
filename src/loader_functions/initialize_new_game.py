import tcod as tcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from elements.entity import Entity
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from render_functions import RenderOrder


def get_constants():
    window_title = 'Roguelike Tutorial Revised'

    font_file = './resources/fonts/arial12x12.png'
    font_style = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 5
    max_rooms = 30

    fov_algorithm = tcod.FOV_SHADOW
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50)
    }

    constants = {
        'font_file': font_file,
        'font_style': font_style,
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'colors': colors
    }

    return constants


def get_game_variables(constants):
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, blocks_movement=True, render_order=RenderOrder.ACTOR)
    player.set_appearance('@', tcod.white, 'Player')
    player.set_combat_info(fighter_component)
    player.set_inventory(inventory_component)
    player.set_level(Level())
    entities = [player]

    game_map = GameMap(constants['map_width'], constants['map_height'],
                       constants['room_min_size'], constants['room_max_size'])
    entities.extend(game_map.make_map(constants['max_rooms'], player))

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state
