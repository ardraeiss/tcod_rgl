import tcod

from elements.entity import Entity, get_blocking_entities_at_location
from elements.world import World
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import Render, RenderOrder
from components.fighter import Fighter
from death_functions import kill_monster, kill_player


class Game:
    """Game session object"""
    title = 'tcod tutorial revised'
    fullscreen = False

    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2

    fov_radius = 4

    def __init__(self) -> None:
        tcod.console_set_custom_font('./resources/fonts/arial12x12.png',
                                     tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

        self.world = World()

        fighter_component = Fighter(hp=30, defense=2, power=5)
        self.game_map = GameMap(self.map_width, self.map_height, self.room_min_size, self.room_max_size)

        self.player = Entity(x=int(self.screen_width / 2), y=int(self.screen_height / 2),
                             char='@', color=tcod.white, name="Player",
                             fighter=fighter_component, render_order=RenderOrder.ACTOR)

        self.entities = self.game_map.make_map(self.max_rooms, self.player, self.max_monsters_per_room)
        self.entities.append(self.player)

        self.fov_map = initialize_fov(self.game_map)

        self.game_state = GameStates.PLAYERS_TURN

        # TODO extract console handler class
        self.main_console = tcod.console_init_root(
                self.screen_width,
                self.screen_height,
                self.title,
                self.fullscreen,
                order="F")
        self.draw_buffer = tcod.console_new(self.screen_width, self.screen_height)
        self.render = Render(self.main_console, self.draw_buffer, self.game_map,
                             self.screen_width, self.screen_height)

        self.player_turn_results = []

    def run(self) -> bool:
        print("Running")

        fov_light_walls = True
        fov_algorithm = tcod.FOV_SHADOW

        fov_recompute = True

        key = tcod.Key()
        mouse = tcod.Mouse()

        while not tcod.console_is_window_closed():
            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

            if fov_recompute:
                recompute_fov(self.fov_map, self.player.x, self.player.y,
                              self.fov_radius, fov_light_walls, fov_algorithm)
                fov_recompute = False

            self.render.render_all(self.entities, self.player, self.fov_map,)

            action = handle_keys(key)
            a_exit = action.get('exit')
            a_fullscreen = action.get('fullscreen')
            fov_recompute |= self.change_light_radius(action)

            if a_exit:
                return True

            if a_fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            if self.game_state == GameStates.PLAYERS_TURN:
                fov_recompute |= self.move_player(action)

            self.flush_turn_log()

            if self.game_state == GameStates.ENEMY_TURN:
                self.do_entities_actions()

    def flush_turn_log(self):
        for player_turn_result in self.player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                print(message)

            if dead_entity:
                if dead_entity == self.player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                print(message)

        self.player_turn_results = []

    def do_entities_actions(self):
        for entity in self.entities:
            if entity.ai:
                enemy_turn_results = entity.ai.take_turn(self.player, self.fov_map, self.game_map, self.entities)

                for enemy_turn_result in enemy_turn_results:
                    message = enemy_turn_result.get('message')
                    dead_entity = enemy_turn_result.get('dead')

                    if message:
                        print(message)

                    if dead_entity:
                        if dead_entity == self.player:
                            message, self.game_state = kill_player(dead_entity)
                        else:
                            message = kill_monster(dead_entity)

                        print(message)

                    if self.game_state == GameStates.PLAYER_DEAD:
                        break

            if self.game_state == GameStates.PLAYER_DEAD:
                break

        if self.game_state != GameStates.PLAYER_DEAD:
            self.game_state = GameStates.PLAYERS_TURN

    def change_light_radius(self, action) -> bool:
        a_light_radius = action.get('light_radius')
        if not a_light_radius:
            return False
        self.fov_radius = min(10, max(1, self.fov_radius + a_light_radius))
        return True

    def move_player(self, action) -> bool:
        fov_recompute = False

        rest = action.get('rest')
        if rest:
            self.game_state = GameStates.ENEMY_TURN
            return False

        a_move = action.get('move')
        if not a_move:
            return False

        dx, dy = a_move
        destination_x = self.player.x + dx
        destination_y = self.player.y + dy
        if not self.game_map.is_blocked(destination_x, destination_y):
            target = get_blocking_entities_at_location(self.entities, destination_x, destination_y)
            if target and target.ai:
                attack_results = self.player.fighter.attack(target)
                self.player_turn_results.extend(attack_results)
            else:
                self.player.move(dx, dy)
                fov_recompute = True

        self.game_state = GameStates.ENEMY_TURN
        return fov_recompute
