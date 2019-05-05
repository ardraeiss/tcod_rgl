
class Entity:
    def __init__(self, x, y, char, color, name):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
