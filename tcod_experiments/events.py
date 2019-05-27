import tcod.event


class State(tcod.event.EventDispatch):
    def ev_quit(self, event):
        raise SystemExit()

    def ev_keydown(self, event):
        if event.repeat:
            return
        print(event)

    def ev_keyup(self, event):
        if event.repeat:
            return
        print(event)

    def ev_mousebuttondown(self, event):
        print(event)

    def ev_mousemotion(self, event):
        print(event)


tcod.console_set_custom_font('./resources/fonts/arial12x12.png',
                             tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
root_console = tcod.console_init_root(80, 60)
state = State()
while True:
    for event in tcod.event.wait():
        state.dispatch(event)
