import unittest
import mycroft
import socketserver
import io
import threading
import sys


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


class MockServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class MycroftAppTestCase(unittest.TestCase):

    def client_handler(self, request, client_address, server):
        self.app_connection = request

    def setUp(self):
        sys.argv.append('--no-tls')
        self.server = MockServer(('localhost', 8070), self.client_handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
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
        if hasattr(self, 'app_connection'):
            self.app_connection.close()
        self.server.shutdown()
        self.server.server_close()


class TestStartup(MycroftAppTestCase):

    def test_start(self):
        self.app.start(
            name='TestApp',
            manifest=self.manifest,
            port=8070,
            host='localhost',
        )
