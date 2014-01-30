import asyncore, socket, re, json, uuid

class MycroftClient(asynccore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.dependencies = {}

    def handle_connect(self):
        print('Connected to Mycroft')
        send_manifest()
        on_connect()

    def handle_read(self):
        length = int(recv_until_newline())
        message = recv(length)
        parsed = parse_message(message)
        print('Recieved {0}'.format(parsed))
        if parsed['type'] == 'APP_MANIFEST_OK' or parsed['type'] == 'APP_MANIFEST_FAIL':
            check_manifest(parsed)
            self.verified = True
        on_data(parsed)

    def handle_close(self):
        on_end()
        down()
        print('Disconnected from Mycroft')
        self.close()

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

    # Sends app down to mycroft
    def down(self):
        send_message('APP_DOWN')

    # Sends app in use to mycroft
    def in_use(self, priority=None):
        send_message('APP_IN_USE', {'priority': priority or 30})

    # Sends a query to mycroft
    def query(self, capability, action, data, instance_id=[], priority=30):
        query_message = {
            'id': uuid.uuid4(),
            'capability': capability,
            'action': action,
            'data': data,
            'priority': priority,
            'instanceId': instance_id
        }

        send_message('MSG_QUERY', query_message)

    # Sends query success to mycroft
    def query_success(self, message_id, ret):
        query_success_message = {
            'id': message_id,
            'ret': ret
        }

        send_message('MSG_QUERY_SUCCESS', query_success_message)

    # Sends query fail to mycroft
    def query_fail(self, message_id, message):
        query_fail_message = {
            'id': message_id,
            'message': message
        }

        send_message('MSG_QUERY_FAIL', query_fail_message)

    # Send broadcast to mycroft
    def broadcast(self, content):
        message = {
            'id': uuid.uuid4(),
            'content': content
        }

        send_message('MSG_BROADCAST', message)

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

    def recv_until_newline(self):
        message = ""
        while True:
            chunk = self.recv(1)
            if chunk == "" or chunk == "\n":
                break
            message += chunk
        return message