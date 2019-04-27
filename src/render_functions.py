import tcod


colors = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
}


def render_all(main_console, console, entities, game_map, screen_width, screen_height):
    # Draw map tiles
    for y in range(game_map.height):
        for x in range(game_map.width):
            wall = game_map.tiles[x][y].block_sight

            if wall:
                console.bg[y, x] = colors['dark_wall']
            else:
                console.bg[y, x] = colors['dark_ground']

    # Draw all entities
    for entry in entities:
        draw_entity(console, entry)

    tcod.console_blit(console, 0, 0, screen_width, screen_height, main_console, 0, 0)

    tcod.console_flush()

    # clean console space
    clean_all(console, entities)


def clean_all(console, entities):
    # Remove all entities from screen
    for entry in entities:
        clear_entity(console, entry)


def draw_entity(console, entry):
    # put entity character on screen
    tcod.console_put_char_ex(console, entry.x, entry.y, entry.char, entry.color, tcod.black)


def clear_entity(console, entry):
    # erase the entity character
    tcod.console_put_char_ex(console, entry.x, entry.y, ' ', entry.color, tcod.black)


