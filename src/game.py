import tcod

from elements.entity import get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.data_loaders import load_game, save_game
from loader_functions.initialize_new_game import get_constants, get_game_variables
from menu import main_menu, message_box
from render_functions import Render
from death_functions import kill_monster, kill_player


class Game:
    """Game session object"""
    fullscreen = False

    def __init__(self) -> None:
        self.constants = get_constants()

        self.fov_radius = self.constants['fov_radius']

        tcod.console_set_custom_font(self.constants['font_file'], self.constants['font_style'])

        self.targeting_item = None

        # TODO extract console handler class
        self.main_console = tcod.console_init_root(
                self.constants['screen_width'],
                self.constants['screen_height'],
                self.constants['window_title'],
                self.fullscreen,
                order="F")
        self.map_buffer = tcod.console.Console(self.constants['screen_width'], self.constants['screen_height'])
        self.panel_buffer = tcod.console.Console(self.constants['screen_width'], self.constants['screen_height'])

        self.player = None
        self.entities = None
        self.game_map = None
        self.message_log = None
        self.game_state = None
        self.fov_map = None

        self.previous_game_state = GameStates.PLAYERS_TURN

        self.render = None
        self.render = Render(self.main_console, self.constants['screen_width'], self.constants['screen_height'],
                             self.constants['colors'])

        self.reset_game()

        self.player_turn_results = []

    def reset_game(self):
        self.player, self.entities, self.game_map, self.message_log, self.game_state = \
            get_game_variables(self.constants)

    def run(self):
        show_main_menu = True
        show_load_error_message = False

        main_menu_background_image = tcod.image_load('menu_background.png')

        key = tcod.Key()
        mouse = tcod.Mouse()

        while not tcod.console_is_window_closed():
            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

            if show_main_menu:
                main_menu(self.main_console, main_menu_background_image, self.constants['screen_width'],
                          self.constants['screen_height'])

                if show_load_error_message:
                    message_box(self.main_console, 'No save game to load', 50,
                                self.constants['screen_width'], self.constants['screen_height'])

                tcod.console_flush()

                action = handle_main_menu(key)

                new_game = action.get('new_game')
                load_saved_game = action.get('load_game')
                exit_game = action.get('exit')

                if show_load_error_message and (new_game or load_saved_game or exit_game):
                    show_load_error_message = False
                elif new_game:
                    self.reset_game()
                    show_main_menu = False
                elif load_saved_game:
                    try:
                        self.player, self.entities, self.game_map, self.message_log, self.game_state = load_game()
                        show_main_menu = False
                    except FileNotFoundError:
                        show_load_error_message = True
                elif exit_game:
                    break

            else:
                tcod.console_clear(self.main_console)
                self.play_game()

                show_main_menu = True

    def play_game(self) -> bool:
        print("Running")

        self.game_state = GameStates.PLAYERS_TURN
        self.previous_game_state = GameStates.PLAYERS_TURN

        self.render.set_map(self.game_map, self.map_buffer)
        self.render.set_panel(self.panel_buffer, self.constants['panel_height'],
                              self.constants['bar_width'], self.constants['panel_y'])

        self.render.set_message_log(self.message_log)

        self.targeting_item = None

        self.fov_radius = self.constants['fov_radius']
        self.fov_map = initialize_fov(self.game_map)

        self.player_turn_results = []

        fov_recompute = True

        key = tcod.Key()
        mouse = tcod.Mouse()

        while not tcod.console_is_window_closed():
            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

            fov_recompute = self.recompute_fov(fov_recompute)

            self.render.render_all(self.entities, self.player, self.fov_map, mouse, self.game_state)

            action = handle_keys(key, self.game_state)
            mouse_action = handle_mouse(mouse)

            left_click = mouse_action.get('left_click')
            right_click = mouse_action.get('right_click')

            fov_recompute |= self.change_light_radius(action)

            self.do_inventory(action)

            self.do_targeting(left_click, right_click)

            a_take_stairs = action.get('take_stairs')
            a_exit = action.get('exit')
            if a_exit:
                if self.game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                    self.game_state = self.previous_game_state
                elif self.game_state == GameStates.TARGETING:
                    self.player_turn_results.append({'targeting_cancelled': True})
                else:
                    save_game(self.player, self.entities, self.game_map, self.message_log, self.game_state)

                    return True

            if a_take_stairs and self.game_state == GameStates.PLAYERS_TURN:
                stairs = next((e for e in self.entities if e.stairs), None)
                if stairs and stairs.x == self.player.x and stairs.y == self.player.y:
                    self.entities = self.game_map.next_floor(self.player, self.message_log, self.constants)
                    self.fov_map = initialize_fov(self.game_map)
                    fov_recompute = True
                    self.render.game_map = self.game_map

                    tcod.console_clear(self.main_console)

                else:
                    self.message_log.add_message(Message('There are no stairs here.', tcod.yellow))

            a_fullscreen = action.get('fullscreen')
            if a_fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            fov_recompute = self.do_player_turn(action, fov_recompute)

            self.evaluate_messages()

            if self.game_state == GameStates.ENEMY_TURN:
                self.do_entities_actions()

    def recompute_fov(self, fov_recompute):
        if fov_recompute:
            recompute_fov(self.fov_map, self.player.x, self.player.y,
                          self.fov_radius, self.constants['fov_light_walls'], self.constants['fov_algorithm'])
            fov_recompute = False
        return fov_recompute

    def do_player_turn(self, action, fov_recompute):
        if self.game_state == GameStates.PLAYERS_TURN:
            fov_recompute |= self.move_player(action)
            fov_recompute |= self.interact(action)
        return fov_recompute

    def do_inventory(self, action):
        a_show_inventory = action.get('show_inventory')
        if a_show_inventory:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.SHOW_INVENTORY
        a_drop_inventory = action.get('drop_inventory')
        if a_drop_inventory:
            self.previous_game_state = self.game_state
            self.game_state = GameStates.DROP_INVENTORY
        a_inventory_index = action.get('inventory_index')
        if a_inventory_index is not None:
            self.handle_inventory(a_inventory_index)

    def do_targeting(self, left_click, right_click):
        if self.game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = self.player.inventory.use(
                    self.targeting_item, entities=self.entities, fov_map=self.fov_map,
                    target_x=target_x, target_y=target_y)
                self.player_turn_results.extend(item_use_results)
            elif right_click:
                self.player_turn_results.append({'targeting_cancelled': True})

    def handle_inventory(self, a_inventory_index):
        if self.previous_game_state != GameStates.PLAYER_DEAD and a_inventory_index < len(self.player.inventory.items):
            item = self.player.inventory.items[a_inventory_index]

            if self.game_state == GameStates.SHOW_INVENTORY:
                inventory_results = self.player.inventory.use(item, entities=self.entities, fov_map=self.fov_map)
                self.player_turn_results.extend(inventory_results)
            elif self.game_state == GameStates.DROP_INVENTORY:
                inventory_results = self.player.inventory.drop_item(item)
                self.player_turn_results.extend(inventory_results)

    def evaluate_messages(self):
        for player_turn_result in self.player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_dropped = player_turn_result.get('item_dropped')
            item_consumed = player_turn_result.get('consumed')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                self.message_log.add_message(message)

            self.evaluate_dead_entity(dead_entity)

            if item_added:
                self.pick_up_item(item_added)
            elif item_dropped:
                self.drop_item(item_dropped)
            elif item_consumed:
                self.use_item(item_consumed)
            elif targeting:
                self.previous_game_state = GameStates.PLAYERS_TURN
                self.game_state = GameStates.TARGETING

                self.targeting_item = targeting

                self.message_log.add_message(self.targeting_item.item.targeting_message)
            elif targeting_cancelled:
                self.game_state = self.previous_game_state

                self.message_log.add_message(Message('Targeting cancelled'))
        self.player_turn_results = []

    def pick_up_item(self, item_added):
        self.entities.remove(item_added)

        self.game_state = GameStates.ENEMY_TURN

    def use_item(self, item_consumed):
        self.game_state = GameStates.ENEMY_TURN

    def drop_item(self, item_dropped):
        self.entities.append(item_dropped)
        self.game_state = GameStates.ENEMY_TURN

    def do_entities_actions(self):
        for entity in self.entities:
            if entity.ai:
                enemy_turn_results = entity.ai.take_turn(self.player, self.fov_map, self.game_map, self.entities)

                for enemy_turn_result in enemy_turn_results:
                    message = enemy_turn_result.get('message')
                    dead_entity = enemy_turn_result.get('dead')

                    if message:
                        self.message_log.add_message(message)

                    self.evaluate_dead_entity(dead_entity)

                    if self.game_state == GameStates.PLAYER_DEAD:
                        return

        if self.game_state != GameStates.PLAYER_DEAD:
            self.game_state = GameStates.PLAYERS_TURN

    def evaluate_dead_entity(self, dead_entity):
        if not dead_entity:
            return

        if dead_entity == self.player:
            message, self.game_state = kill_player(dead_entity)
        else:
            message = kill_monster(dead_entity)

        self.message_log.add_message(message)

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

    def interact(self, action) -> bool:
        fov_recompute = False

        pickup = action.get('pickup')
        if not pickup:
            return False

        entity = next(
            (e for e in self.entities if e.item and e.x == self.player.x and e.y == self.player.y),
            None)
        if entity:
            pickup_results = self.player.inventory.add_item(entity)
            self.player_turn_results.extend(pickup_results)
            fov_recompute = True
        else:
            self.message_log.add_message(Message('There is nothing here to pick up.', tcod.yellow))

        return fov_recompute
