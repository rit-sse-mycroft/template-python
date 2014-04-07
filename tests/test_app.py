import unittest
import mycroft
import socketserver
import io
import threading
import sys
import logging
import time
from functools import wraps
import errno
import os
import signal
import json


class MockApp(mycroft.App):

    def __init__(self):
        self.fired_events = {}

    @mycroft.on('connect')
    def connect(self, body=None):
        self.fired_events['connect'] = True

    @mycroft.on('end')
    def end(self, body=None):
        self.fired_events['end'] = True

    @mycroft.on('error')
    def error(self, body=None):
        self.fired_events['error'] = True

    @mycroft.on('event_loop')
    def ev_loop(self, body=None):
        self.fired_events['event_loop'] = True

    def on_foo(self, body):
        self.fired_events['FOO'] = body


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
        self.manifest_str = """
        {
            "this is a totally": "not valid manifest",
            "but_its": 1323,
            "only for": "testing"
        }
        """
        self.manifest = io.StringIO(self.manifest_str)

    def tearDown(self):
        try:
            try:
                self.app.close()
            except IOError:
                pass
            except AttributeError:
                pass
            try:
                if hasattr(self, 'app_connection'):
                    self.app_connection.close()
            except IOError:
                pass
            self.server.shutdown()
            self.server.server_close()
        finally:
            self.closing = True


class TestStartup(MycroftAppTestCase):

    def test_start(self):
        def start_app_thread():
            self.app.start(
                name='TestApp',
                manifest=self.manifest,
                port=8070,
                host='localhost',
                silent=True
            )
        self.app_thread = threading.Thread(target=start_app_thread)
        self.app_thread.start()
        time.sleep(0.5)
        self.assertTrue('connect' in self.app.fired_events)
        self.assertFalse('end' in self.app.fired_events)
        self.assertFalse('error' in self.app.fired_events)
        self.assertTrue('event_loop' in self.app.fired_events)

        content = self.app_connection.recv(100).decode('utf-8')
        self.assertEqual(
            '96\nAPP_MANIFEST ' + json.dumps(json.loads(self.manifest_str)),
            content
        )


class TestAppHandler(MycroftAppTestCase):

    def test_msg_handling(self):
        def start_app_thread():
            self.app.start(
                name='TestApp',
                manifest=self.manifest,
                port=8070,
                host='localhost',
                silent=True
            )
        self.app_thread = threading.Thread(target=start_app_thread)
        self.app_thread.start()
        time.sleep(0.4)
        self.app_connection.send(b'15\nFOO {"thing":1}')
        time.sleep(0.4)
        self.assertTrue('FOO' in self.app.fired_events)
        self.assertEqual(
            {"thing": 1},
            self.app.fired_events['FOO']
        )
