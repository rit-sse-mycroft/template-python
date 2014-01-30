import socket, re, json, uuid, sys, ssl

class MycroftClient():

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(sys.argv) == 1:
            self.socket = ssl.wrap_socket(self.socket, keyfile=key_path, certfile=cert_path)
        self.socket.connect((host,port))
        self.handle_connect()
        self.dependencies = {}

    def event_loop(self):
        while True:
            self.handle_read()

    def handle_connect(self):
        print('Connected to Mycroft')
        self.send_manifest()
        self.connected = True
        self.on_connect()

    def handle_read(self):
        length = int(self.recv_until_newline())
        message = str(self.socket.recv(length),encoding='UTF-8')
        parsed = self.parse_message(message)
        print('Recieved {0}'.format(parsed))
        if parsed['type'] == 'APP_MANIFEST_OK' or parsed['type'] == 'APP_MANIFEST_FAIL':
            self.check_manifest(parsed)
            self.verified = True
        self.on_data(parsed)

    def handle_close(self):
        self.on_end()
        self.down()
        print('Disconnected from Mycroft')
        self.socket.close()

    # Sends App Manifest to mycroft
    def send_manifest(self):
        f = open(self.manifest)
        message = json.loads(f.read())
        self.send_message('APP_MANIFEST', message)

    # Checks if manifest is valid
    def check_manifest(self, parsed):
        if parsed['type'] == 'APP_MANIFEST_OK':
            print('Manifest Validated')
        elif(parsed['type'] == 'APP_MANIFEST_FAIL'):
            raise Exception("Invalid Application Manifest")

    # Sends app up to mycroft
    def up(self):
        self.send_message('APP_UP')

    # Sends app down to mycroft
    def down(self):
        self.send_message('APP_DOWN')

    # Sends app in use to mycroft
    def in_use(self, priority=None):
        self.send_message('APP_IN_USE', {'priority': priority or 30})

    # Sends a query to mycroft
    def query(self, capability, action, data, instance_id=[], priority=30):
        query_message = {
            'id': str(uuid.uuid4()),
            'capability': capability,
            'action': action,
            'data': data,
            'priority': priority,
            'instanceId': instance_id
        }

        self.send_message('MSG_QUERY', query_message)

    # Sends query success to mycroft
    def query_success(self, message_id, ret):
        query_success_message = {
            'id': message_id,
            'ret': ret
        }

        self.send_message('MSG_QUERY_SUCCESS', query_success_message)

    # Sends query fail to mycroft
    def query_fail(self, message_id, message):
        query_fail_message = {
            'id': message_id,
            'message': message
        }

        self.send_message('MSG_QUERY_FAIL', query_fail_message)

    # Send broadcast to mycroft
    def broadcast(self, content):
        message = {
            'id': str(uuid.uuid4()),
            'content': content
        }

        self.send_message('MSG_BROADCAST', message)

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
        print('Sending Message')
        print(str(length))
        print(body)
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

    def start(self):
        try:
            self.event_loop()
        finally:
            self.handle_close()