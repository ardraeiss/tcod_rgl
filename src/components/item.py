

class Item:
    def __init__(self, use_function=None, **kwargs):
        self.owner = None
        self.use_function = use_function
        self.function_kwargs = kwargs

    def set_owner(self, owner):
        self.owner = owner
