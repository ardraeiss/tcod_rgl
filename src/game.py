import tcod

from elements.entity import Entity
from elements.world import World
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all


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

        self.player = Entity(int(self.screen_width / 2), int(self.screen_height / 2), '@', tcod.white)
        self.npc = Entity(int(self.screen_width / 2)-2, int(self.screen_height / 2)+5, 'r', tcod.dark_green)
        self.entities = [self.npc, self.player]

    def run(self) -> bool:
        print("Running")

        # TODO extract console handler class
        main_console = tcod.console_init_root(
                self.screen_width,
                self.screen_height,
                self.title,
                self.fullscreen,
                order="F")
        console = tcod.console_new(self.screen_width, self.screen_height)
        console.print_(x=0, y=0, string='Hello World!')

        game_map = GameMap(self.map_width, self.map_height)
        game_map.make_map()

        key = tcod.Key()
        mouse = tcod.Mouse()

        while not tcod.console_is_window_closed():
            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

            render_all(main_console, console, self.entities, game_map, self.screen_width, self.screen_height)

            action = handle_keys(key)
            a_move = action.get('move')
            a_exit = action.get('exit')
            a_fullscreen = action.get('fullscreen')

            if a_exit:
                return True

            if a_move:
                dx, dy = a_move
                if not game_map.is_blocked(self.player.x + dx, self.player.y + dy):
                    self.player.move(dx, dy)
                if not game_map.is_blocked(self.npc.x + dx, self.npc.y):
                    self.npc.move(dx, 0)

            if a_fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
