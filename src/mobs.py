from typing import Dict

import tcod

from components.fighter import Fighter
from components.ai import BasicMonster
from elements.entity import Entity
from random_utils import from_dungeon_level
from render_functions import RenderOrder


MONSTER_DATA = {
    'orc': {
        'display_name': "Orc",
        'display_char': 'o',
        'display_color': tcod.desaturated_green,
        'ai': 'basic',
        'fighter': {
            'hp': 20,
            'defense': 0,
            'power': 4,
        },
        'reward': {
            'experience': 35,
        },
        'levels': ((40, 1), (80, 2)),
    },
    'kobold': {
        'display_name': "Kobold",
        'display_char': 'k',
        'display_color': tcod.desaturated_green,
        'ai': 'basic',
        'fighter': {
            'hp': 10,
            'defense': 0,
            'power': 3,
        },
        'reward': {
            'experience': 25,
        },
        'levels': ((80, 1), (40, 3), (20, 4), (0, 5)),
    },
    'ogre': {
        'display_name': "Ogre",
        'display_char': 'O',
        'display_color': tcod.desaturated_green,
        'ai': 'basic',
        'fighter': {
            'hp': 25,
            'defense': 1,
            'power': 6,
        },
        'reward': {
            'experience': 75,
        },
        'levels': ((20, 2), (15, 4), (0, 6)),
        'boss': True,
    },
    'troll': {
        'display_name': "Troll",
        'display_char': 'T',
        'display_color': tcod.darker_green,
        'ai': 'basic',
        'fighter': {
            'hp': 30,
            'defense': 2,
            'power': 8,
        },
        'reward': {
            'experience': 100,
        },
        'levels': ((15, 3), (30, 5), (60, 7)),
    },
    'red_dragon': {
        'display_name': "Young Red Dragon",
        'display_char': 'd',
        'display_color': tcod.light_flame,
        'ai': 'basic',
        'fighter': {
            'hp': 45,
            'defense': 4,
            'power': 12,
        },
        'reward': {
            'experience': 200,
        },
        'levels': ((5, 5), (10, 6), (15, 7)),
        'boss': True,
    },
}

MAX_MONSTERS_PER_ROOM_BY_DEPTH = ((2, 1), (3, 4), (5, 6))
BOSSES_NUMBER_BY_DEPTH = ((1, 2), (2, 5), (3, 7), (5, 8), (8, 9))

MONSTER_CHANCES_BY_DEPTH = {
    'kobold': [[80, 1], [40, 3], [20, 4], [0, 5]],
    'orc': [[40, 1], [80, 2]],
    'troll': [[15, 3], [30, 5], [60, 7]],
    'ogre': [[20, 2], [15, 4], [0, 6]],
    'red_dragon': [[5, 5], [10, 6], [15, 7]],
}

BOSS_MONSTERS = tuple(name for name, value in MONSTER_DATA.items() if value.get('boss', False))


def spawn_regular_monster(x: int, y: int, name: str) -> [Entity, None]:
    data = MONSTER_DATA.get(name)
    if not data:
        return None

    fighter = Fighter(
        data['fighter']['hp'],
        data['fighter']['defense'],
        data['fighter']['power'],
        data['reward']['experience'],
    )

    ai = BasicMonster()
    monster = Entity(x, y, render_order=RenderOrder.ACTOR, components={
        'ai': ai,
        'fighter': fighter,
    })
    monster.set_appearance(
        data['display_char'],
        data['display_color'],
        data['display_name'],
    )

    return monster


def get_monster_chances_by_depth(dungeon_level: int) -> Dict:
    result = dict()
    for name, value in MONSTER_DATA:
        weight = from_dungeon_level(value['levels'], dungeon_level)
        if weight > 0:
            continue
        result[name] = weight

    return result

