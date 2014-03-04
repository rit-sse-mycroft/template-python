import json
import re


class HelpersMixin:
    # Parses a message
    def parse_message(self, msg):
        regex = re.compile('([A-Z_]*) ({.*})$')
        match = regex.match(msg)
        if match is None:
            regex = re.compile('([A-Z_]*)')
            match = regex.match(msg)
            if match is None:
                raise Exception('Error: Malformed Message')
            msg_type = match.groups()[0]
            data = {}
        else:
            msg_type = match.groups()[0]
            data = json.loads(match.groups()[1])
        return {'type': msg_type, 'data': data}

    # Sends a message of a specific type
    def send_message(self, msg_type, message=None):
        message = '' if message is None else json.dumps(message)
        body = msg_type + ' ' + message
        body = body.strip()
        length = len(body)
        self.logger.info('Sending Message')
        self.logger.debug(str(length) + ' ' + (body))
        string = "{0}\n{1}".format(length, body)
        self.socket.send(bytes(string, 'UTF-8'))

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