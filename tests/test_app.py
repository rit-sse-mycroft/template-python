import unittest
import mycroft
import socketserver
import io
import threading
import sys
import logging
import time


class MockApp(mycroft.App):

    def __init__(self):
        self.fired_events = {}

    @mycroft.on(
        'before_connect',
        'after_connect',
        'before_send_manifest',
        'after_send_manifest',
        'before_event_loop',
        'before_read',
        'after_read',
        'before_handle_close',
        'after_handle_close',
        'end',
        'APP_MANIFEST_OK',
        'MSG_QUERY')
    def record_event(self, ev_name, data=None):
        self.fired_events[ev_name] = True

    @mycroft.on('before_connect')
    def set_null_logger(self, ev_name):
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers = []


class MockServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class MycroftAppTestCase(unittest.TestCase):

    def client_handler(self, request, client_address, server):
        self.app_connection = request

    def setUp(self):
        sys.argv.append('--no-tls')
        self.closing = False

        class MockServerHandler(socketserver.BaseRequestHandler):
            def handle(inner_self):
                self.app_connection = inner_self.request
                # keep the connection open
                while not self.closing:
                    pass

        self.server = MockServer(('localhost', 8070), MockServerHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.app = MockApp()
        self.manifest = io.StringIO("""
        {
            "this is a totally": "not valid manifest",
            "but_its": 1323,
            "only for": "testing"
        }
        """)

    def tearDown(self):
        try:
            self.app.close()
        except IOError:
            pass
        try:
            if hasattr(self, 'app_connection'):
                self.app_connection.close()
        except IOError:
            pass
        self.closing = True
        self.server.shutdown()
        self.server.server_close()


class TestStartup(MycroftAppTestCase):

    def test_start(self):
        def start_app_thread():
            self.app.start(
                name='TestApp',
                manifest=self.manifest,
                port=8070,
                host='localhost',
            )
        self.app_thread = threading.Thread(target=start_app_thread)
        self.app_thread.start()
        time.sleep(1)
