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
        'end')
    def record_event(self, ev_name, body=None):
        self.fired_events[ev_name] = True

    def on_foo(self, ev_name, body):
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
        time.sleep(0.4)
        self.assertTrue('before_connect' in self.app.fired_events)
        self.assertTrue('after_connect' in self.app.fired_events)
        self.assertTrue('before_send_manifest' in self.app.fired_events)
        self.assertTrue('after_send_manifest' in self.app.fired_events)
        self.assertTrue('before_event_loop' in self.app.fired_events)
        self.assertTrue('before_read' in self.app.fired_events)
        self.assertFalse('after_read' in self.app.fired_events)
        self.assertFalse('before_handle_close' in self.app.fired_events)
        self.assertFalse('after_handle_close' in self.app.fired_events)
        self.assertFalse('end' in self.app.fired_events)

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
