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
