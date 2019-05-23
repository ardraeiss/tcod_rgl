import tcod


def menu(main_console, header, options, width, screen_width, screen_height):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = main_console.get_height_rect(0, 0, width, screen_height, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tcod.console_new(width, height)

    # print the header, with auto-wrap
    window.default_bg = tcod.white
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '({}) {}'.format(chr(letter_index), option_text)
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    # tcod.console_blit(window, 0, 0, width, height, main_console, x, y, 1.0, 0.7)
    window.blit(main_console, x, y, 0, 0, width, height, 1.0, 0.7)


def inventory_menu(main_console, header, inventory, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(main_console, header, options, inventory_width, screen_width, screen_height)


def main_menu(con, background_image, screen_width, screen_height):
    tcod.image_blit_2x(background_image, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.light_yellow)
    tcod.console_print_ex(con, int(screen_width / 2), int(screen_height / 2) - 4, tcod.BKGND_NONE, tcod.CENTER,
                          'TOMBS OF THE ANCIENT KINGS')
    tcod.console_print_ex(con, int(screen_width / 2), int(screen_height - 2), tcod.BKGND_NONE, tcod.CENTER,
                          'By (Your name here)')

    menu(con, '', ['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height)


def level_up_menu(main_console, header, player, menu_width, screen_width, screen_height):
    options = ['Constitution (+20 HP, from {0})'.format(player.fighter.max_hp),
               'Strength (+1 attack, from {0})'.format(player.fighter.power),
               'Agility (+1 defense, from {0})'.format(player.fighter.defense)]

    menu(main_console, header, options, menu_width, screen_width, screen_height)


def character_screen(player, character_screen_width, character_screen_height, screen_width, screen_height):
    window = tcod.console_new(character_screen_width, character_screen_height)

    tcod.console_set_default_foreground(window, tcod.white)

    tcod.console_print_rect_ex(window, 0, 1, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Character Information')
    tcod.console_print_rect_ex(window, 0, 2, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Level: {0}'.format(player.level.current_level))
    tcod.console_print_rect_ex(window, 0, 3, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Experience: {0}'.format(player.level.current_xp))
    tcod.console_print_rect_ex(window, 0, 4, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Experience to Level: {0}'.format(
            player.level.experience_to_next_level-player.level.current_xp))
    tcod.console_print_rect_ex(window, 0, 6, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Maximum HP: {0}'.format(player.fighter.max_hp))
    tcod.console_print_rect_ex(window, 0, 7, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Attack: {0}'.format(player.fighter.power))
    tcod.console_print_rect_ex(window, 0, 8, character_screen_width, character_screen_height, tcod.BKGND_NONE,
                               tcod.LEFT, 'Defense: {0}'.format(player.fighter.defense))

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    tcod.console_blit(window, 0, 0, character_screen_width, character_screen_height, 0, x, y, 1.0, 0.7)


def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
