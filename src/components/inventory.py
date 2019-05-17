

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        self.owner = None

    def set_owner(self, owner):
        self.owner = owner
