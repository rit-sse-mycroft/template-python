import socket, sys, ssl, messages, helpers

class MycroftClient(HelpersMixin, MessagesMixin):

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(sys.argv) == 1:
            self.socket = ssl.wrap_socket(self.socket, keyfile=key_path, certfile=cert_path)
        self.socket.connect((host,port))
        self.handle_connect()
        self.dependencies = {}
        self.handlers = EventHandlers()

    def on(msg_type, func):
        handlers[k] = func

    def event_loop(self):
        while True:
            self.handle_read()

    def handle_connect(self):
        print('Connected to Mycroft')
        self.send_manifest()
        self.handlers(self, 'connect')

    def handle_read(self):
        length = int(self.recv_until_newline())
        message = str(self.socket.recv(length),encoding='UTF-8')
        parsed = self.parse_message(message)
        print('Recieved {0}'.format(parsed))
        self.handlers(self, parsed['type'], parsed['data'])
        if parsed['type'] == 'APP_MANIFEST_OK' or parsed['type'] == 'APP_MANIFEST_FAIL':
            self.check_manifest(parsed)
            self.verified = True

    def handle_close(self):
        self.handlers(self, 'end')
        self.down()
        print('Disconnected from Mycroft')
        self.socket.close()

    def start(self):
        try:
            self.event_loop()
        finally:
            self.handle_close()

    def app_manifest_ok(self, msg_type, data ):
        self.verified = True
        puts 'Manifest Verified'

    def app_manifest_fail(self, msg_type, data):
        raise Exception('Invalid application manifest')

    self.on('APP_MANIFEST_OK', app_manifest_ok)
    self.on('APP_MANIFEST_FAIL', app_manifest_fail)