import json
import string


class HelpersMixin:

    # Parses a message
    def parse_message(self, msg):
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

    # Sends a message of a specific type
    def send_message(self, msg_type, message=None):
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

    # Updates dependencies
    def update_dependencies(self, deps):
        for capability, instance in deps.iteritems():
            self.dependencies[capability] = self.dependencies[capability] or {}
            for appId, status in instance.iteritems():
                self.dependencies[capability][appId] = status

    def recv_until_newline(self):
        message = ""
        while True:
            chunk = str(self.socket.recv(1), encoding='UTF-8')
            if chunk == "" or chunk == '\n':
                break
            message += chunk
        return message
