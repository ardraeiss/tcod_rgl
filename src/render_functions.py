import tcod

from enum import Enum, auto

from game_states import GameStates
from menu import inventory_menu, level_up_menu, character_screen


class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


_colors = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50),
}


class Render:
    def __init__(self, main_console, screen_width, screen_height, colors):
        self.main_console = main_console
        self.map_buffer = None
        self.panel_buffer = None
        self.game_map = None
        self.message_log = None
        self.screen_width, self.screen_height = screen_width, screen_height
        self.panel_height = 0
        self.panel_width = 1
        self.panel_y = self.screen_height - 1
        self.bar_color = tcod.light_red
        self.back_color = tcod.darker_red

        self.colors = colors

    def set_map(self, game_map, map_buffer):
        self.game_map = game_map
        self.map_buffer = map_buffer

    def set_panel(self, panel_buffer, panel_height, panel_width, panel_y):
        self.panel_buffer = panel_buffer
        self.panel_height = panel_height
        self.panel_width = panel_width
        self.panel_y = panel_y

    def set_message_log(self, message_log):
        self.message_log = message_log

    def render_all(self, entities, player, fov_map, mouse, game_state):
        # Draw map tiles
        self.draw_tiles(fov_map)

        # Draw all entities
        entities_in_render_order = sorted(entities, key=lambda e: e.render_order.value)

        for entry in entities_in_render_order:
            self.draw_entity(entry, fov_map)

        tcod.console_print_ex(self.map_buffer, 1, self.screen_height - 2, tcod.BKGND_NONE, tcod.LEFT,
                              'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp))

        tcod.console_blit(self.map_buffer, 0, 0, self.screen_width, self.screen_height,
                          self.main_console, 0, 0)

        # draw UI
        self.panel_buffer.default_bg = tcod.black
        self.panel_buffer.clear()

        # Print the game messages, one line at a time
        y = 1
        for message in self.message_log.messages:
            tcod.console_set_default_foreground(self.panel_buffer, message.color)
            tcod.console_print_ex(self.panel_buffer, self.message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
            y += 1

        self.render_bar(1, 1, 'HP', player.fighter.hp, player.fighter.max_hp)
        tcod.console_print_ex(self.panel_buffer, 1, 3, tcod.BKGND_NONE, tcod.LEFT,
                              'Dungeon level: {0}'.format(self.game_map.dungeon_level))

        if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY,
                          GameStates.LEVEL_UP, GameStates.CHARACTER_SCREEN):
            self.render_menu(game_state, player)

        tcod.console_set_default_foreground(self.panel_buffer, tcod.light_gray)
        tcod.console_print_ex(self.panel_buffer, 1, 0, tcod.BKGND_NONE, tcod.LEFT,
                              get_names_under_mouse(mouse, entities, fov_map))

        tcod.console_blit(self.panel_buffer, 0, 0, self.screen_width, self.panel_height,
                          self.main_console, 0, self.panel_y)

        tcod.console_flush()

        # clean console space
        self.clean_all(entities)

    def render_bar(self, x, y, name, value, maximum):
        bar_width = int(float(value) / maximum * self.panel_width)

        self.panel_buffer.default_bg = self.back_color
        tcod.console_rect(self.panel_buffer, x, y, self.panel_width, 1, False, tcod.BKGND_SCREEN)

        self.panel_buffer.default_bg = self.bar_color
        if bar_width > 0:
            self.panel_buffer.rect(x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

        self.panel_buffer.default_fg = tcod.white
        health_text = '{0}: {1}/{2}'.format(name, value, maximum)
        tcod.console_print_ex(self.panel_buffer,
                              int(x + self.panel_width / 2), y,
                              tcod.BKGND_NONE, tcod.CENTER,
                              health_text)

    def draw_tiles(self, fov_map):
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                visible = fov_map.fov[y, x]

                color = self.get_tile_colors(self.game_map.tiles[x][y], visible)

                if visible:
                    self.game_map.tiles[x][y].explored = True

                self.map_buffer.bg[y, x] = color

    def render_menu(self, game_state, player):
        if game_state == GameStates.SHOW_INVENTORY:
            text = "Press the key next to an item to use it, or Esc to cancel.\n"
            inventory_menu(self.main_console, text,
                           player, 50, self.screen_width, self.screen_height)
        elif game_state == GameStates.DROP_INVENTORY:
            text = "Press the key net to an item to drop it, or Esc to cancel.\n"
            inventory_menu(self.main_console, text,
                           player, 50, self.screen_width, self.screen_height)
        elif game_state == GameStates.LEVEL_UP:
            level_up_menu(self.main_console, 'Level up! Choose a stat to raise:',
                          player, 40, self.screen_width, self.screen_height)
        elif game_state == GameStates.CHARACTER_SCREEN:
            character_screen(player, 30, 10, self.screen_width, self.screen_height)

    def get_tile_colors(self, tile, visible: bool) -> tcod.Color:
        if visible:
            if tile.block_sight:
                return self.colors['light_wall']
            return self.colors['light_ground']
        elif tile.explored:
            if tile.block_sight:
                return self.colors['dark_wall']
            return self.colors['dark_ground']
        return tcod.Color(0, 0, 0)

    def clean_all(self, entities):
        # Remove all entities from screen
        for entry in entities:
            self.clear_entity(entry)

    def draw_entity(self, entry, fov_map):
        # put entity character on screen
        if fov_map.fov[entry.y, entry.x] or (entry.stairs and self.game_map.tiles[entry.x][entry.y].explored):
            tcod.console_put_char_ex(self.map_buffer, entry.x, entry.y, entry.char, entry.color, tcod.black)

    def clear_entity(self, entry):
        # erase the entity character
        tcod.console_put_char_ex(self.map_buffer, entry.x, entry.y, ' ', entry.color, tcod.black)


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and fov_map.fov[entity.y, entity.x]]
    names = ', '.join(names)

    return names.capitalize()
