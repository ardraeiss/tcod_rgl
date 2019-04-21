import tcod as libtcod


class Engine:
    screen_width = 80
    screen_height = 50

    def __init__(self):
        pass

    def __str__(self):
        return "Engine"

    def run(self):
        print("Running")

        libtcod.console_set_custom_font('./resources/fonts/arial12x12.png',
                                        libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

        console = libtcod.console_init_root(self.screen_width, self.screen_height, 'libtcod tutorial revised', False)
        print("Console {}".format(console))

        while not libtcod.console_is_window_closed():
            libtcod.console_set_default_foreground(console, libtcod.white)
            libtcod.console_put_char(console, 1, 1, '@', libtcod.BKGND_NONE)
            libtcod.console_flush()

            key = libtcod.console_check_for_keypress()

            if key.vk == libtcod.KEY_ESCAPE:
                return True
