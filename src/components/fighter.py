import tcod

from game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power, xp=0):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.owner = None
        self.xp = xp

    def set_owner(self, owner):
        self.owner = owner

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        damage = self.power - target.fighter.defense

        if not target.is_alive():
            print("{} kicks the dead body of {}".format(self.owner.name.capitalize(), target.name))

        else:
            if damage > 0:
                results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                    self.owner.name.capitalize(), target.name, str(damage)), tcod.white)})
                results.extend(target.fighter.take_damage(damage))

            else:
                results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                    self.owner.name.capitalize(), target.name), tcod.white)})

        return results
