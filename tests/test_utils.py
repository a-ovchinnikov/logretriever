# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

try:
    import StringIO
except ImportError:
    import io as StringIO
import sys
import types
import os
import unittest

import logretriever.utils as utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.old_stderr = sys.stderr
        sys.stderr = self.new_stderr = StringIO.StringIO()

    def tearDown(self):
        sys.stderr = self.old_stderr

    def test_parse_line_ok(self):
        line = ('127.0.0.1 - foo [01/Jul/2000:00:00:00 +0000] '
                '"GET /foo HTTP/1.0" 200 100')
        expected = utils.log_line(
            '127.0.0.1', '-', 'foo',
            '01/Jul/2000:00:00:00 +0000',
            utils.request_line('GET', '/foo', 'HTTP/1.0'),
            '200', '100')

        actual = utils.parse_line(line)

        self.assertEqual(expected, actual)

    def test_parse_line_malformed(self):
        line = ('127.0.0.1 - [01/Jul/2000:00:00:00 +0000] '
                '"GET /foo HTTP/1.0" 200 100')
        expected = None

        actual = utils.parse_line(line)

        self.assertEqual(expected, actual)

    def test_parse_line_other(self):
        line = 'spam'
        expected = None

        actual = utils.parse_line(line)

        self.assertEqual(expected, actual)

    def test_get_fresh_events_ok(self):
        data_in = 'spam\nfoo\nbar\n'
        fakefile = StringIO.StringIO(data_in)
        expected = data_in.split('\n')[1:-1]

        fakefile.seek(5)
        actual = utils.get_fresh_events(fakefile)

        self.assertEqual(expected, actual)

    def test_get_fresh_events_truncated(self):
        data_in = 'spam\nfoo\nbar\n'
        fakefile = StringIO.StringIO(data_in)
        expected1 = data_in.split('\n')[:-1]
        expected2 = [data_in.split('\n')[0]]

        actual1 = utils.get_fresh_events(fakefile)
        fakefile.seek(0)
        fakefile.truncate(5)
        actual2 = utils.get_fresh_events(fakefile)

        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2, actual2)

    def test_get_fresh_events_no_events(self):
        data_in = ''
        fakefile = StringIO.StringIO(data_in)
        expected = []

        actual = utils.get_fresh_events(fakefile)

        self.assertEqual(expected, actual)

    def test_get_fresh_events_partial(self):
        data_in = 'spam\nfoo\nbar\nbaz'
        fakefile = StringIO.StringIO(data_in)
        expected = data_in.split('\n')[1:-1]

        fakefile.seek(5)
        actual = utils.get_fresh_events(fakefile)

        self.assertEqual(expected, actual)

    def test_load_ok(self):
        # TODO: replace with Mock when the fate of dependecies and Py2
        # version is clear.
        getopt = lambda self, *x: 'foo, bar'
        fake_config = type('Fcon', (object,), {})
        fake_config.get = types.MethodType(getopt, fake_config)
        fake_module = type('Fmod', (object,),
                           {'foo': lambda self, *x: 'spam',
                            'bar': lambda self, *x: 'quux'})()
        expected = ['spam', 'quux']

        actual = utils.load(fake_config, 'baz', fake_module)

        self.assertEqual(expected, actual)

    def test_load_not_ok(self):
        expected_stderr = 'ERROR: No baz could be found in module meep\n'
        getopt = lambda self, *x: 'foo, baz'
        getbool = lambda self, *x: False
        fake_config = type('Fcon', (object,), {})
        fake_config.get = types.MethodType(getopt, fake_config)
        fake_config.getboolean = types.MethodType(getbool, fake_config)
        fake_module = type('Fmod', (object,),
                           {'foo': lambda self, *x: 'spam',
                            'bar': lambda self, *x: 'quux',
                            '__name__': 'meep'})()

        with self.assertRaises(SystemExit):
            utils.load(fake_config, 'baz', fake_module)
        self.assertEqual(expected_stderr, self.new_stderr.getvalue())

    def test_load_not_ok_unsafe(self):
        expected_stderr = 'WARNING: No baz could be found in module meep\n'
        expected = ['spam']
        getopt = lambda self, *x: 'foo, baz'
        getbool = lambda self, *x: True
        fake_config = type('Fcon', (object,), {})
        fake_config.get = types.MethodType(getopt, fake_config)
        fake_config.getboolean = types.MethodType(getbool, fake_config)
        fake_module = type('Fmod', (object,),
                           {'foo': lambda self, *x: 'spam',
                            'bar': lambda self, *x: 'quux',
                            '__name__': 'meep'})()

        actual = utils.load(fake_config, 'baz', fake_module)

        self.assertEqual(expected_stderr, self.new_stderr.getvalue())
        self.assertEqual(expected, actual)

    def test_file_has_problems_notfound(self):
        os.path.isfile = lambda *x: False
        expected_stderr = 'ERROR: File not found: /foo/bar.baz\n'

        result = utils.file_has_problems('/foo/bar.baz')

        self.assertTrue(result)
        self.assertEqual(expected_stderr, self.new_stderr.getvalue())

    def test_file_has_problems_noaccess(self):
        os.path.isfile = lambda *x: True
        os.access = lambda *x: False
        expected_stderr = 'ERROR: Permission denied: /foo/bar.baz\n'

        result = utils.file_has_problems('/foo/bar.baz')

        self.assertTrue(result)
        self.assertEqual(expected_stderr, self.new_stderr.getvalue())

    def test_file_has_problems_no_problems(self):
        os.path.isfile = lambda *x: True
        os.access = lambda *x: True

        result = utils.file_has_problems('/foo/bar.baz')

        self.assertFalse(result)
