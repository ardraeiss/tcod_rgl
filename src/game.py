import tcod
from world import World
from character import Character


class Game:
    """Game session object"""
    screen_width = 80
    screen_height = 50

    def __init__(self) -> None:
        self.world = World()
        self.player = Character((int(self.screen_width / 2), int(self.screen_height / 2)), '@')

    def run(self) -> bool:
        print("Running")

        # TODO extract console handler class
        tcod.console_set_custom_font('./resources/fonts/arial12x12.png',
                                     tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

        console = tcod.console_init_root(self.screen_width, self.screen_height, 'tcod tutorial revised', False)

        while not tcod.console_is_window_closed():
            tcod.console_set_default_foreground(console, tcod.white)
            self.player.draw(console)
            # tcod.console_put_char(console, self.player.x, self.player.y, '@', tcod.BKGND_NONE)
            tcod.console_flush()

            key = tcod.console_check_for_keypress()

            if key.vk == tcod.KEY_ESCAPE:
                return True
