

class BasicMonster:
    def __init__(self):
        self.owner = None

    def set_owner(self, owner):
        self.owner = owner

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        if fov_map.fov[monster.y, monster.x]:
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.is_alive():
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results
