import tcod


colors = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50),
}


def render_all(main_console, console, entities, game_map, fov_map, screen_width, screen_height):
    # Draw map tiles
    for y in range(game_map.height):
        for x in range(game_map.width):
            visible = fov_map.fov[y, x]
            wall = game_map.tiles[x][y].block_sight

            if visible:
                if wall:
                    console.bg[y, x] = colors['light_wall']
                else:
                    console.bg[y, x] = colors['light_ground']
            else:
                if wall:
                    console.bg[y, x] = colors['dark_wall']
                else:
                    console.bg[y, x] = colors['dark_ground']

    # Draw all entities
    for entry in entities:
        draw_entity(console, entry, fov_map)

    tcod.console_blit(console, 0, 0, screen_width, screen_height, main_console, 0, 0)

    tcod.console_flush()

    # clean console space
    clean_all(console, entities)


def clean_all(console, entities):
    # Remove all entities from screen
    for entry in entities:
        clear_entity(console, entry)


def draw_entity(console, entry, fov_map):
    # put entity character on screen
    if fov_map.fov[entry.y, entry.x]:
        tcod.console_put_char_ex(console, entry.x, entry.y, entry.char, entry.color, tcod.black)


def clear_entity(console, entry):
    # erase the entity character
    tcod.console_put_char_ex(console, entry.x, entry.y, ' ', entry.color, tcod.black)


