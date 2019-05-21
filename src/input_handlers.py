import tcod

from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)

    if game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)

    if game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)

    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)

    # Movement keys
    movement_res = handle_movement_keys(key)
    if movement_res:
        return movement_res

    if key_char == 'g':
        return {'pickup': True}

    if key_char == 'i':
        return {'show_inventory': True}
    if key_char == 'd':
        return {'drop_inventory': True}

    if key.vk == tcod.KEY_KPADD or (key_char == '=' and key.shift):
        return {'light_radius': 1}
    if key.vk == tcod.KEY_KPSUB or (key_char == '-' and not key.shift):
        return {'light_radius': -1}

    if key.vk in (tcod.KEY_ENTER, tcod.KEY_KPENTER) and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


def handle_movement_keys(key):
    if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
        return {'move': (0, -1)}
    if key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
        return {'move': (0, 1)}
    if key.vk in (tcod.KEY_LEFT, tcod.KEY_KP4):
        return {'move': (-1, 0)}
    if key.vk in (tcod.KEY_RIGHT, tcod.KEY_KP6):
        return {'move': (1, 0)}
    if key.vk == tcod.KEY_KP7:
        return {'move': (-1, -1)}
    if key.vk == tcod.KEY_KP9:
        return {'move': (1, -1)}
    if key.vk == tcod.KEY_KP3:
        return {'move': (1, 1)}
    if key.vk == tcod.KEY_KP1:
        return {'move': (-1, 1)}
    if key.vk == tcod.KEY_KP5:
        return {'rest': (True, 1)}
    return {}


def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}

    if key.vk in (tcod.KEY_ENTER, tcod.KEY_KPENTER) and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key.vk in (tcod.KEY_ENTER, tcod.KEY_KPENTER) and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_targeting_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}


def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}
