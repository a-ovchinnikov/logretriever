# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

import types
import unittest

import logretriever.utils as utils
import logretriever.collectors as collectors


class TestSimpleCollector(unittest.TestCase):

    def setUp(self):
        values = {'alarm_interval': 2, 'statistics_interval': 1,
                  'alarm_threshold': 2}
        getint = lambda self, _, x: values[x]
        has_section = lambda self, *x: True
        self.fake_config = type('Fcon', (object,), {})
        self.fake_config.getint = types.MethodType(getint, self.fake_config)
        self.fake_config.has_section = types.MethodType(has_section,
                                                        self.fake_config)
        self.collector = collectors.SimpleCollector(self.fake_config)
        self.alarm = ''
        self.collector.set_alarm_callback(self.set_alarm)

    def set_alarm(self, x):
        self.alarm = ' '.join(x.split(' ')[2:])

    def test_alarm_happens(self):
        expected = ': '.join(self.collector.lh_msg.split(': ')[1:]) % {'hr': 2}

        self.collector.process_line('foo')
        self.collector.process_line('foo')
        self.collector.tick()
        self.collector.process_line('foo')
        self.collector.process_line('foo')
        self.collector.tick()

        self.assertEqual(expected, self.alarm)

    def test_alarm_goes_away(self):
        expected1 = ': '.join(self.collector.lh_msg.split(': ')[1:]) % {
            'hr': 2}
        expected2 = ': '.join(self.collector.hl_msg.split(': ')[1:])

        self.collector.process_line('foo')
        self.collector.process_line('foo')
        self.collector.tick()
        self.collector.process_line('foo')
        self.collector.process_line('foo')
        self.collector.tick()

        self.assertEqual(expected1, self.alarm)

        self.collector.process_line('foo')
        self.collector.tick()

        self.assertEqual(expected2, self.alarm)

    def test_get_stats(self):
        expected = self.collector.stat_msg % 1

        self.collector.process_line('foo')
        self.collector.tick()

        actual = self.collector.get_stats()

        self.assertEqual(expected, actual)
