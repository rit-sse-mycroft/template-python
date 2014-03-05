import socket
import sys
import ssl
import logging
import os
from logging import handlers
from mycroft import helpers, event, messages, logger

_LOG_FORMAT = "[$BOLD%(asctime)-20s$RESET] [%(levelname)-18s]  %(message)s"
_COLOR_FORMAT = logger.formatter_message(_LOG_FORMAT, True)


class App(helpers.HelpersMixin, messages.MessagesMixin):
    """
    Superclass for Mycroft applications.

    Mycroft can fire the following event names:
      internal events:
        'before_connect' - fired before connection is attempted
        'after_connect' - fired after connection is acheived
        'before_send_manifest' - fired before manifest is to be sent
        'after_send_manifest' - fired after manifest is sent
        'before_event_loop' - fired before the event loop is started
        'before_read' - before waiting for the next message
        'after_read' - fired after the most recent message was processed
        'before_handle_close' - fired after the app must close but before
                                cleanup is done
        'after_handle_close' - fired after the close is handled
        'end' - fired, if possible, when start() is returning
      external events:
        any verb from Mycroft, such as
        'APP_MANIFEST_OK'
        'APP_MANIFEST_FAIL'
        etc ...
    """

    def start(
            self,
            manifest,
            host='localhost',
            port=1847,
            key_path='',
            cert_path=''):
        """
        Start this App.
        This attempts to connect to Mycroft.
        If connection is successful it sends APP_MANIFEST.
        Args:
            manifest - str, the path to this application's manifest
            host - str, the host to connect to (default 'localhost')
            port - int, the port to connect to (default 1847)
            key_path - str, path to the keyfile
            cert_path - str, path to the crt file
        """
        try:
            self.manifest = manifest
            self.dependencies = {}
            self.setup_logger()
            self.setup_handlers(self.logger)
            self.handlers('before_connect', fail_silently=True)
            self.setup_socket(
                '--no-tls' not in sys.argv,
                host=host,
                port=port,
                key_path=key_path,
                cert_path=cert_path
            )
            self.handlers('after_connect', fail_silently=True)
            self.handlers('before_send_manifest', fail_silently=True)
            self.logger.info('Sending Manifest', fail_silently=True)
            self.send_manifest()
            self.handlers('after_send_manifest', fail_silently=True)
            self.handlers('before_event_loop', fail_silently=True)
            try:
                self.event_loop()
            finally:
                self.handlers('before_handle_close', fail_silently=True)
                self.handle_close()
                self.handlers('after_handle_close', fail_silently=True)
        finally:
            self.handlers('end')

    def setup_logger(self):
        """
        Setup the logger.
        Assigns the logger to `self.logger`
        """
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        color_formatter = logger.ColoredFormatter(_COLOR_FORMAT)
        regular_formatter = logging.Formatter(
            '[%(asctime)-20s][%(levelname)-5s]  %(message)s'
        )
        try:
            os.mkdir('logs')
        except OSError:
            pass
        file_handler = handlers.TimedRotatingFileHandler(
            "{0}/{1}.log".format('logs', self.name),
            'midnight'
        )
        file_handler.setFormatter(regular_formatter)
        self.logger.addHandler(file_handler)

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(color_formatter)
        self.logger.addHandler(console)

    def setup_socket(
            self,
            use_tls=False,
            host='localhost',
            port=1847,
            key_path='',
            cert_path=''):
        """
        Setup the socket connection to Mycroft
        The socket is assigned to `self.socket`
        Args:
            use_tls - bool, True to use TLS (default False)
            host - string, host to use for connecting (default 'localhost')
            port - int, port to connect to (default 1847)
            key_path - string, file path to the keyfile
            cert_path - string, file path to the certificate file
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if use_tls:
            self.socket = ssl.wrap_socket(
                self.socket,
                keyfile=key_path,
                certfile=cert_path
            )
        self.socket.connect((host, port))

    def setup_handlers(self):
        """
        Construct the event handling object.
        The object is assigned to `self.handlers`
        Methods that are added by default:
            -any methods that are registered with the @mycroft.on('')
             decorator
            -methods that start with on_*** (event name is ***)
        """
        self.handlers = event.EventHandler(self.logger)
        for attr_name, val in self.__dict__.items():
            # handle the first type of event registration
            if hasattr(val, '_mycroft_events'):
                for ev_name in val._mycroft_events:
                    self.handlers[ev_name] = val
            # handle the second type of event registration
            elif (attr_name.startswith('on') and
                  attr_name != 'on' and
                  hasattr(val, '__call__')):
                self.handlers[attr_name[3:]] = val

    def on(self, ev_name, func):
        """
        Add a function to the record of handlers
        Args:
            ev_name: str, the type of message to which this responds
            func: function, what to call for responding to this message
        """
        self.handlers[ev_name] = func

    def event_loop(self):
        """
        Loops forever listening for messages
        """
        while True:
            self.handlers('before_read', self)
            self.handle_read()
            self.handlers('after_read', self)

    def handle_read(self):
        """
        Handle one message
        """
        length = int(self.recv_until_newline())
        message = str(self.socket.recv(length), encoding='UTF-8')
        parsed = self.parse_message(message)
        self.logger.info('Got {0}'.format(parsed['type']))
        self.logger.debug(parsed['data'])
        self.handlers(
            parsed['type'],
            body=parsed['data'],
        )

    def handle_close(self):
        self.down()
        self.logger.info('Disconnected from Mycroft')
        self.socket.close()

    def on_app_manifest_ok(self, verb,  body):
        self.verified = True
        self.logger.info('Manifest Verified')

    def on_app_manifest_fail(self, verb, body):
        self.logger.error('Invalid application manifest')
        raise Exception('Invalid application manifest')

    def on_message_general_failure(self, verb, body):
        self.logger.error(data['message'])
