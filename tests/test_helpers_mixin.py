import unittest
from mycroft import helpers


class MockSocket():
    """
    Mocks a Python socket
    """

    def __init__(self):
        self.bytes = b''

    def send(self, bytes_):
        self.bytes += bytes_


class TestParseMessage(unittest.TestCase):

    def test_msg_with_body(self):
        helper = helpers.HelpersMixin()
        msg = """
        VERB_NAME {
                "a_key": "a value",
                "another key": 12345,
                "this_is_a_dict": {"this": "thing"},
                "a_float": 1.2
        }"""
        parsed = helper.parse_message(msg)
        self.assertEqual(
            'VERB_NAME',
            parsed['type']
        )
        self.assertEqual(
            'a value',
            parsed['data']['a_key']
        )
        self.assertEqual(
            12345,
            parsed['data']['another key']
        )
        self.assertEqual(
            {'this': 'thing'},
            parsed['data']['this_is_a_dict']
        )
        self.assertEqual(
            1.2,
            parsed['data']['a_float']
        )

    def test_msg_without_body(self):
        helper = helpers.HelpersMixin()
        msg = 'QUERY'
        parsed = helper.parse_message(msg)
        self.assertEqual(
            'QUERY',
            parsed['type']
        )
        self.assertEqual(
            None,
            parsed['data']
        )
        msg = 'thisShouldntparse'
        with self.assertRaises(ValueError):
            helper.parse_message(msg)

    def test_malformed_msg(self):
        helper = helpers.HelpersMixin()
        msg = 'MSG_QUERY {this isn\'t valid json}'
        with self.assertRaises(ValueError):
            helper.parse_message(msg)
        msg = ''
        with self.assertRaises(ValueError):
            helper.parse_message(msg)


class TestSendMessage(unittest.TestCase):

    def test_send_with_body(self):
        helper = helpers.HelpersMixin()
        mock_socket = MockSocket()
        helper.socket = mock_socket
        # send a message w/ the snowman character, bonus utf8 test!
        helper.send_message(
            'VERB',
            {'this is': '☃'}
        )

        expected_body = 'VERB {"this is": "\\u2603"}'
        num_bytes = len(expected_body.encode('utf-8'))
        expected_body = str(num_bytes) + '\n' + expected_body
        bytes_expected = expected_body.encode('utf-8')

        self.assertEqual(
            bytes_expected,
            mock_socket.bytes
        )

    def test_send_without_body(self):
        helper = helpers.HelpersMixin()
        mock_socket = MockSocket()
        helper.socket = mock_socket
        helper.send_message('VERB')

        expected = 'VERB'
        num_bytes = len(expected.encode('utf-8'))
        expected = str(num_bytes) + '\n' + expected
        bytes_expected = expected.encode('utf-8')

        self.assertEqual(
            bytes_expected,
            mock_socket.bytes
        )


class TestUpdateDependencies(unittest.TestCase):

    def test_empty_dependencies(self):
        helper = helpers.HelpersMixin()
        helper.dependencies = {}
        helper.update_dependencies({})
        self.assertEqual(
            {},
            helper.dependencies
        )

    def test_unset_dependencies(self):
        helper = helpers.HelpersMixin()
        helper.dependencies = {}
        helper.update_dependencies({
            'cap1': {
                'inst1': 'up',
                'inst2': 'down'
            }
        })
        self.assertEqual(
            {
                'cap1': {
                    'inst1': 'up',
                    'inst2': 'down'
                }
            },
            helper.dependencies
        )

    def test_update_dependencies(self):
        helper = helpers.HelpersMixin()
        helper.dependencies = {
            'cap1': {
                'inst1': 'up',
                'inst2': 'down'
            },
            'cap2': {
                'cap2inst': 'down'
            }
        }
        helper.update_dependencies({
            'cap1': {
                'inst1': 'down',
                'inst3': 'up'
            }
        })
        self.assertEqual(
            {
                'cap1': {
                    'inst1': 'down',
                    'inst2': 'down',
                    'inst3': 'up'
                },
                'cap2': {
                    'cap2inst': 'down'
                }
            },
            helper.dependencies
        )
