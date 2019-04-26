import tcod

from elements.entity import Entity
from elements.world import World
from input_handlers import handle_keys


class Game:
    """Game session object"""
    screen_width = 80
    screen_height = 50
    title = 'tcod tutorial revised'
    fullscreen = False

    def __init__(self) -> None:
        tcod.console_set_custom_font('./resources/fonts/arial12x12.png',
                                     tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

        self.world = World()

    def run(self) -> bool:
        print("Running")

        # TODO extract console handler class
        with tcod.console_init_root(
                self.screen_width,
                self.screen_height,
                self.title,
                self.fullscreen,
                order="F") as main_console:
            console = tcod.console_new(self.screen_width, self.screen_height)
            console.print_(x=0, y=0, string='Hello World!')
            player = Entity(int(self.screen_width / 2), int(self.screen_height / 2), '@', tcod.white)
            npc = Entity(int(self.screen_width / 2)-2, int(self.screen_height / 2)+5, '@', tcod.yellow)
            entities = [npc, player]

            key = tcod.Key()
            mouse = tcod.Mouse()

            while not tcod.console_is_window_closed():
                tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

                for entry in entities:
                    tcod.console_put_char_ex(console, entry.x, entry.y, entry.char, fore=entry.color, back=tcod.black)

                tcod.console_blit(console, 0, 0, self.screen_width, self.screen_height, main_console, 0, 0)
                tcod.console_flush()

                # clean console space
                for entry in entities:
                    tcod.console_put_char(console, entry.x, entry.y, ' ', tcod.BKGND_NONE)

                action = handle_keys(key)
                a_move = action.get('move')
                a_exit = action.get('exit')
                a_fullscreen = action.get('fullscreen')

                if a_exit:
                    return True

                if a_move:
                    dx, dy = a_move
                    player.move(dx, dy)
                    npc.move(dx, 0)

                if a_fullscreen:
                    tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
