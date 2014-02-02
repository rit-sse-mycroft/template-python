class Events:
    def __init__(self):
        self.handlers = {}

    def __setitem__(self, k, handler):
        if k not in self.handlers:
            self.handlers[k] = []
        self.handlers[k].append(handler)
        return self

    def __call__(self, sender, event, data):
        if(event in self.handlers):
            for handler in self.handlers[event]:
                handler(sender, event, data)
        else:
            print("Not handling message: {0}".format(event))
