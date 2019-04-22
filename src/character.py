import tcod


class Character:
    def __init__(self, position, char):
        self.x, self.y = position
        self.char = char
        self.char_mode = tcod.BKGND_NONE

    def draw(self, console):
        tcod.console_put_char(console, self.x, self.y, self.char, self.char_mode)
