import tcod


def render_all(main_console, console, entities, screen_width, screen_height):
    # Draw all entities
    for entry in entities:
        draw_entity(console, entry)

    tcod.console_blit(console, 0, 0, screen_width, screen_height, main_console, 0, 0)


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


