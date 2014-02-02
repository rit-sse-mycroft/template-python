class EventHandlers:
    def __init__(self):
        self.handlers = {}

    def __setitem__(self, k, handler):
        if k not in self.handlers:
            self.handlers[k] = []
        self.handlers[k].append(handler)
        return self

    def __call__(self, sender, msg_type, data=None):
        if(msg_type in self.handlers):
            for handler in self.handlers[msg_type]:
                handler(sender, msg_type, data)
        else:
            print("Not handling message: {0}".format(msg_type))
