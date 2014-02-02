import socket, sys, ssl
from mycroft import helpers, event, messages

class MycroftClient(helpers.HelpersMixin, messages.MessagesMixin):

    def __init__(self, host, port, manifest, key_path='', cert_path=''):
        self.manifest = manifest
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(sys.argv) == 1:
            self.socket = ssl.wrap_socket(self.socket, keyfile=key_path, certfile=cert_path)
        self.socket.connect((host,port))
        self.dependencies = {}
        self.handlers = event.EventHandlers()
        self.on('APP_MANIFEST_OK', self.app_manifest_ok)
        self.on('APP_MANIFEST_FAIL', self.app_manifest_fail)
        self.handle_connect()

    def on(self, msg_type, func):
        self.handlers[msg_type] = func

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

    def app_manifest_ok(self, sender, msg_type, data ):
        self.verified = True
        print('Manifest Verified')

    def app_manifest_fail(self, sender, msg_type, data):
        raise Exception('Invalid application manifest')