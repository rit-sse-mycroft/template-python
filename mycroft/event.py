class EventHandler:
    """
    A class to keep track of event handlers
    """

    def __init__(self, logger):
        """
        Create a new EventHandler
        Args:
            logger - the logger to use
        """
        self.handlers = {}
        self.logger = logger

    def __setitem__(self, k, handler):
        """
        Set the handler for an action.
        This is called via `handlers[k] = handler`
        Args:
            k - the key to use for this handler
            handler - func, what handles this event
        """
        if k not in self.handlers:
            self.handlers[k] = []
        self.handlers[k].append(handler)
        return self

    def __call__(self, sender, msg_type, data=None):
        """
        Call the handlers for a message
        Args:

        """
        if msg_type in self.handlers:
            for handler in self.handlers[msg_type]:
                handler(sender, msg_type, data)
        else:
            self.logger.warning("Not handling message: {0}".format(msg_type))
