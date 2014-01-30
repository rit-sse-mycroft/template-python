import asyncore, socket, re, json

class MycroftClient(asynccore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.dependencies = {}

    def handle_connect(self):
        pass

    def handle_read(self):
        pass

    def handle_close(self):
        pass

    # Sends App Manifest to mycroft
    def send_manifest(self):
        f = open(self.manifest)
        manifest = json.loads(f.read())
        send_message('APP_MANIFEST', message)

    # Checks if manifest is valid
    def check_manifest(self, parsed):
        if parsed['type'] == 'APP_MANIFEST_OK':
            print('Manifest Validated')
        elif(parsed['type'] == 'APP_MANIFEST_FAIL'):
            raise Exception("Invalid Application Manifest")

    # Sends app up to mycroft
    def up(self):
        send_message('APP_UP')

    # Sends app dwon to mycroft
    def down(self):
        send_message('APP_DOWN')

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
        body = type + ' ' + message
        body = body.strip()
        length = len(body)
        print('Sending Message')
        print(str(length))
        print(body)
        self.send("{0}\n{1}".format(length, body))

    # Updates dependencies
    def update_dependencies(self, deps):
        for capability, instance in deps.iteritems():
            self.dependencies[capability] = self.dependencies[capability] or {}
            for appId, status in instance.iteritems():
                self.dependencies[capability][appId] = status