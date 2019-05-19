import tcod

from components.inventory import Inventory
from elements.entity import Entity, get_blocking_entities_at_location
from elements.world import World
from fov_functions import initialize_fov, recompute_fov
from game_messages import MessageLog, Message
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

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2
    max_items_per_room = 3

    fov_radius = 4

    def __init__(self) -> None:
        tcod.console_set_custom_font('./resources/fonts/arial12x12.png',
                                     tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

        self.world = World()

        self.game_map = GameMap(self.map_width, self.map_height, self.room_min_size, self.room_max_size)

        self.player = Entity(x=int(self.screen_width / 2), y=int(self.screen_height / 2),
                             char='@', color=tcod.white, name="Player", render_order=RenderOrder.ACTOR)
        self.player.set_combat_info(Fighter(hp=30, defense=2, power=5))
        self.player.set_inventory(Inventory(26))

        self.entities = self.game_map.make_map(self.max_rooms, self.player,
                                               self.max_monsters_per_room, self.max_items_per_room)
        self.entities.append(self.player)

        self.fov_map = initialize_fov(self.game_map)

        self.game_state = GameStates.PLAYERS_TURN
        self.previous_game_state = GameStates.PLAYERS_TURN

        # TODO extract console handler class
        self.main_console = tcod.console_init_root(
                self.screen_width,
                self.screen_height,
                self.title,
                self.fullscreen,
                order="F")
        self.map_buffer = tcod.console.Console(self.screen_width, self.screen_height)
        self.panel_buffer = tcod.console.Console(self.screen_width, self.panel_height)
        self.render = Render(self.main_console, self.screen_width, self.screen_height)
        self.render.set_map(self.game_map, self.map_buffer)
        self.render.set_panel(self.panel_buffer, self.panel_height, self.bar_width, self.panel_y)

        self.message_log = MessageLog(self.message_x, self.message_width, self.message_height)
        self.render.set_message_log(self.message_log)

        self.player_turn_results = []

    def run(self) -> bool:
        print("Running")

        fov_light_walls = True
        fov_algorithm = tcod.FOV_SHADOW

        fov_recompute = True

        key = tcod.Key()
        mouse = tcod.Mouse()

        while not tcod.console_is_window_closed():
            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

            if fov_recompute:
                recompute_fov(self.fov_map, self.player.x, self.player.y,
                              self.fov_radius, fov_light_walls, fov_algorithm)
                fov_recompute = False

            self.render.render_all(self.entities, self.player, self.fov_map, mouse, self.game_state)

            action = handle_keys(key, self.game_state)
            a_exit = action.get('exit')
            a_fullscreen = action.get('fullscreen')
            a_show_inventory = action.get('show_inventory')
            a_drop_inventory = action.get('drop_inventory')
            a_inventory_index = action.get('inventory_index')
            fov_recompute |= self.change_light_radius(action)

            if a_show_inventory:
                self.previous_game_state = self.game_state
                self.game_state = GameStates.SHOW_INVENTORY

            if a_drop_inventory:
                self.previous_game_state = self.game_state
                self.game_state = GameStates.DROP_INVENTORY

            if a_inventory_index is not None:
                self.handle_inventory(a_inventory_index)

            if a_exit:
                if self.game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                    self.game_state = self.previous_game_state
                else:
                    return True

            if a_fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            if self.game_state == GameStates.PLAYERS_TURN:
                fov_recompute |= self.move_player(action)
                fov_recompute |= self.interact(action)

            self.evaluate_messages()

            if self.game_state == GameStates.ENEMY_TURN:
                self.do_entities_actions()

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

            if message:
                self.message_log.add_message(message)

            self.evaluate_dead_entity(dead_entity)

            if item_added:
                self.pick_up_item(item_added)
            elif item_dropped:
                self.drop_item(item_dropped)
            elif item_consumed:
                self.use_item(item_consumed)

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
