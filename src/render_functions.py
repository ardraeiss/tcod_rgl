import tcod

from enum import Enum


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


colors = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50),
}


class Render:
    def __init__(self, main_console, screen_width, screen_height):
        self.main_console = main_console
        self.map_buffer = None
        self.panel_buffer = None
        self.game_map = None
        self.screen_width, self.screen_height = screen_width, screen_height
        self.panel_height = 0
        self.panel_width = 1
        self.panel_y = self.screen_height - 1
        self.bar_color = tcod.light_red
        self.back_color = tcod.darker_red

    def set_map(self, game_map, map_buffer):
        self.game_map = game_map
        self.map_buffer = map_buffer

    def set_panel(self, panel_buffer, panel_height, panel_width, panel_y):
        self.panel_buffer = panel_buffer
        self.panel_height = panel_height
        self.panel_width = panel_width
        self.panel_y = panel_y

    def render_all(self, entities, player, fov_map):
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

        self.render_bar(1, 1, 'HP', player.fighter.hp, player.fighter.max_hp)

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

    def get_tile_colors(self, tile, visible: bool) -> tcod.Color:
        if visible:
            if tile.block_sight:
                return colors['light_wall']
            return colors['light_ground']
        elif tile.explored:
            if tile.block_sight:
                return colors['dark_wall']
            return colors['dark_ground']
        return tcod.Color(0, 0, 0)

    def clean_all(self, entities):
        # Remove all entities from screen
        for entry in entities:
            self.clear_entity(entry)

    def draw_entity(self, entry, fov_map):
        # put entity character on screen
        if fov_map.fov[entry.y, entry.x]:
            tcod.console_put_char_ex(self.map_buffer, entry.x, entry.y, entry.char, entry.color, tcod.black)

    def clear_entity(self, entry):
        # erase the entity character
        tcod.console_put_char_ex(self.map_buffer, entry.x, entry.y, ' ', entry.color, tcod.black)
