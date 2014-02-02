import socket, sys, ssl, messages, helpers

class MycroftClient(HelpersMixin, MessagesMixin):

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

    def start(self):
        try:
            self.event_loop()
        finally:
            self.handle_close()