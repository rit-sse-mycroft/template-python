class EventHandler:
    """
    A class to keep track of event handlers
    """

    def __init__(self, logger, case_sensitive=False):
        """
        Create a new EventHandler
        Args:
            logger - the logger to use
            case_sensitive - whether event names are sensitive to case
                             (default False)
        """
        self.handlers = {}
        self.case_sensitive = case_sensitive
        self.logger = logger

    def __setitem__(self, k, handler):
        """
        Set the handler for an action.
        This is called via `handlers[k] = handler`
        Args:
            k - the key to use for this handler
            handler - func, what handles this event
        """
        if not self.case_sensitive and hasattr(k, 'lower'):
            k = k.lower()
        if k not in self.handlers:
            self.handlers[k] = []
        self.handlers[k].append(handler)
        return self

    def __call__(self, ev_name, *args, **kwargs):
        """
        Call the handlers for a message.
        Passes arguments after ev_name to the function being called
        Args:
            ev_name - the name of the event to be fired
            fail_silently - when True don't log message if event is unhandled
                            (default False)
        """
        internal_name = ev_name
        if not self.case_sensitive and hasattr(internal_name, 'lower'):
            internal_name = internal_name.lower()
        fail_silently = kwargs.pop('fail_silently', False)
        if internal_name in self.handlers:
            for handler in self.handlers[internal_name]:
                handler(*args, **kwargs)
        elif not fail_silently:
            self.logger.warning("Not handling message: {0}".format(ev_name))
