import socket, sys, ssl, logging, os
from logging import handlers
from mycroft import helpers, event, messages, logger

class MycroftClient(helpers.HelpersMixin, messages.MessagesMixin):
    FORMAT = "[$BOLD%(asctime)-20s$RESET] [%(levelname)-18s]  %(message)s"
    COLOR_FORMAT = logger.formatter_message(FORMAT, True)
    def __init__(self, name, host, port, manifest, key_path='', cert_path=''):
        self.name = name
        self.setup_logger()
        self.manifest = manifest
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(sys.argv) == 1:
            self.socket = ssl.wrap_socket(self.socket, keyfile=key_path, certfile=cert_path)
        self.socket.connect((host,port))
        self.dependencies = {}
        self.handlers = event.EventHandlers(self.logger)
        self.on('APP_MANIFEST_OK', self.app_manifest_ok)
        self.on('APP_MANIFEST_FAIL', self.app_manifest_fail)
        self.on('MSG_GENERAL_FAILURE', self.message_general_failure)
        self.handle_connect()

    def setup_logger(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        color_formatter = logger.ColoredFormatter(self.COLOR_FORMAT)
        regular_formatter = logging.Formatter("[%(asctime)-20s][%(levelname)-5s]  %(message)s")
        try:
            os.mkdir('logs')
        except OSError:
            pass
        file_handler = handlers.TimedRotatingFileHandler("{0}/{1}.log".format('logs', self.name), 'midnight')
        file_handler.setFormatter(regular_formatter)
        self.logger.addHandler(file_handler)

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(color_formatter)
        self.logger.addHandler(console)

    def on(self, msg_type, func):
        self.handlers[msg_type] = func

    def event_loop(self):
        while True:
            self.handle_read()

    def handle_connect(self):
        self.logger.info('Connected to Mycroft')
        self.send_manifest()
        self.handlers(self, 'connect')

    def handle_read(self):
        length = int(self.recv_until_newline())
        message = str(self.socket.recv(length),encoding='UTF-8')
        parsed = self.parse_message(message)
        self.logger.info('Got {0}'.format(parsed['type']))
        self.logger.debug(parsed['data'])
        self.handlers(self, parsed['type'], parsed['data'])

    def handle_close(self):
        self.handlers(self, 'end')
        self.down()
        self.logger.info('Disconnected from Mycroft')
        self.socket.close()

    def start(self):
        try:
            self.event_loop()
        finally:
            self.handle_close()

    def app_manifest_ok(self, sender, msg_type, data ):
        self.verified = True
        self.logger.info('Manifest Verified')

    def app_manifest_fail(self, sender, msg_type, data):
        self.logger.error('Invalid application manifest')
        raise Exception('Invalid application manifest')

    def message_general_failure(self, sender, msg_type, data):
        self.logger.error(data['message'])
