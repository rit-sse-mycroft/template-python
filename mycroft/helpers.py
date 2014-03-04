import json
import string


class HelpersMixin:

    def parse_message(self, msg):
        """
        Parse a supplied message.
        Args:
            msg - a string of the message body (without length)
        Returns:
            {'type':str, 'data':dict}
            the data key may have a null value if this message
            doesn't have a body
        """
        msg = msg.strip()
        if not msg:
            raise ValueError('Message was empty')
        # the verb ends after the first space
        verb_idx = msg.find(' ')
        if verb_idx < 0:
            # there is no body, just return the verb
            data = None
            verb = msg
        else:
            # there is a body, cut it out & parse
            verb = msg[:verb_idx]
            msg = msg[verb_idx+1:]
            msg.strip()
            data = json.loads(msg)
        # make sure verb was formatted correctly
        acceptable = set(string.ascii_uppercase).union(set(string.digits))
        acceptable.add('_')
        for char in verb:
            if char not in acceptable:
                raise ValueError('Verb {0} is not valid'.format(verb))
        return {'type': verb, 'data': data}

    def send_message(self, msg_type, message=None):
        """
        Send a message to Mycroft server
        Args:
            msg_type - str, the verb (ie 'MSG_QUERY')
            message - optional, dict that will be turned into JSON as the body
        None is returned
        """
        if message is not None:
            message = json.dumps(message)
        else:
            message = ''
        body = msg_type + ' ' + message
        body = body.strip()
        length = len(body.encode('utf-8'))
        # don't log if we don't have a logger!
        if hasattr(self, 'logger'):
            self.logger.info('Sending Message')
            self.logger.debug(str(length) + ' ' + (body))
        to_send = "{0}\n{1}".format(length, body)
        self.socket.send(to_send.encode('utf-8'))

    def update_dependencies(self, deps):
        """
        Update the dependencies of this app.
        Args:
            deps - a dictionary of dependencies:
                   {'capability': {'inst_name':'status', ...}, ...}
        None is returned
        """
        for capability, instance in deps.items():
            if not capability in self.dependencies:
                self.dependencies[capability] = {}
            for appId, status in instance.items():
                self.dependencies[capability][appId] = status

    def recv_until_newline(self):
        """
        Read from self.socket until a newline is received
        Returns:
            str, what was read
        """
        message = ""
        while True:
            chunk = str(self.socket.recv(1), encoding='UTF-8')
            if chunk == "" or chunk == '\n':
                break
            message += chunk
        return message
