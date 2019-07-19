# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

import os
try:
    import StringIO
except ImportError:
    import io as StringIO
import sys
import types
import unittest

import logretriever.utils as utils
import logretriever.representers as representers


class TestSimpleRepresenter(unittest.TestCase):

    def setUp(self):
        getint = lambda self, *x: 1
        has_section = lambda self, *x: True
        get_stats = lambda *x: 'fake stats'
        set_alarm_callback = lambda *x: True
        self.fake_config = type('Fcon', (object,), {})
        self.fake_collector = type("Fcol", (object,), {})
        self.fake_config.getint = types.MethodType(getint, self.fake_config)
        self.fake_config.has_section = types.MethodType(has_section,
                                                        self.fake_config)
        self.fake_collector.get_stats = types.MethodType(get_stats,
                                                         self.fake_collector)
        self.fake_collector.set_alarm_callback = (
            types.MethodType(set_alarm_callback, self.fake_collector))
        self.representer = representers.SimpleStatsRepresenter(
            self.fake_config, [self.fake_collector])

    def test_alarm_callback_alarm_ok(self):
        self.representer.alarm_callback('foo')

        self.assertTrue('foo' in self.representer.alarms)

    def test_alarm_callback_alarm_not_ok(self):
        self.representer.alarm_callback('foo')
        self.representer.alarm_callback('foo')

        self.assertFalse('baz' in self.representer.alarms)
        self.assertTrue('foo' in self.representer.alarms)
        self.assertEqual(1, self.representer.alarms.count('foo'))

    def test_show_stats(self):

        os.system = lambda *x: True
        old_stdout = sys.stdout
        sys.stdout = new_stdout = StringIO.StringIO()
        alarm_code = 'foo alarm'

        self.representer.alarm_callback(alarm_code)
        self.representer.show_stats()

        self.assertTrue(alarm_code in new_stdout.getvalue())
        self.assertTrue('fake stats' in new_stdout.getvalue())
