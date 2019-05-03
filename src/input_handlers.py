import tcod


def handle_keys(key):
    # Movement keys
    if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
        return {'move': (0, -1)}
    if key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
        return {'move': (0, 1)}
    if key.vk in (tcod.KEY_LEFT, tcod.KEY_KP4):
        return {'move': (-1, 0)}
    if key.vk in (tcod.KEY_RIGHT, tcod.KEY_KP6):
        return {'move': (1, 0)}

    if key.vk == tcod.KEY_KPADD or key.vk == '+':
        return {'light_radius': 1}
    if key.vk == tcod.KEY_KPSUB or key.vk == '-':
        return {'light_radius': -1}

    if key.vk in (tcod.KEY_ENTER, tcod.KEY_KPENTER) and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}
