import unittest
from mycroft import helpers


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
