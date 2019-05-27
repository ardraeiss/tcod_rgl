

class Item:
    def __init__(self, use_function=None, targeting=False, targeting_message=None, **kwargs):
        self.owner = None
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs

    def set_owner(self, owner):
        self.owner = owner
