from random import randint


def random_choice_index(chances):
    random_chance = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for chance_weight in chances:
        running_sum += chance_weight

        if random_chance <= running_sum:
            return choice
        choice += 1


def random_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())

    return choices[random_choice_index(chances)]


def from_dungeon_level(weights_table, dungeon_level):
    for (value, level) in reversed(weights_table):
        if dungeon_level >= level:
            return value

    return 0
