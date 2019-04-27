import tcod

from elements.entity import Entity
from elements.world import World
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all, clean_all


class Game:
    """Game session object"""
    title = 'tcod tutorial revised'
    fullscreen = False

    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

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

            game_map = GameMap(self.map_width, self.map_height)

            player = Entity(int(self.screen_width / 2), int(self.screen_height / 2), '@', tcod.white)
            npc = Entity(int(self.screen_width / 2)-2, int(self.screen_height / 2)+5, '@', tcod.yellow)
            npc2 = Entity(int(self.screen_width / 2)+5, int(self.screen_height / 2)+1, 'r', tcod.light_grey)
            entities = [npc, player, npc2]

            key = tcod.Key()
            mouse = tcod.Mouse()

            while not tcod.console_is_window_closed():
                tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

                render_all(main_console, console, entities, game_map, self.screen_width, self.screen_height)

                tcod.console_flush()

                # clean console space
                clean_all(console, entities)

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
                    npc2.move(0, dy)

                if a_fullscreen:
                    tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
