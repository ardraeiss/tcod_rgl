

class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.owner = None

    def set_owner(self, owner):
        self.owner = owner

    def take_damage(self, amount):
        self.hp -= amount

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if not target.is_alive():
            print("{} kicks dead body of {}".format(self.owner.name.capitalize(), target.name))
            return

        if damage > 0:
            target.fighter.take_damage(damage)
            print('{0} attacks {1} for {2} hit points. {3} left'.
                  format(self.owner.name.capitalize(), target.name, damage, target.fighter.hp))
            return

        print('{0} attacks {1} but does no damage.'.format(self.owner.name.capitalize(), target.name))
