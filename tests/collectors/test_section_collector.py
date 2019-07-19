# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

import collections
import unittest
import types

import logretriever.utils as utils
import logretriever.collectors as collectors


class TestSectionCollector(unittest.TestCase):

    def setUp(self):
        getint = lambda self, *x: 1
        has_section = lambda self, *x: True
        self.fake_config = type('Fcon', (object,), {})
        self.fake_config.getint = types.MethodType(getint, self.fake_config)
        self.fake_config.has_section = types.MethodType(has_section,
                                                        self.fake_config)
        self.collector = collectors.SectionCollector(self.fake_config)

    def test_process_line(self):
        line = utils.log_line(
            '127.0.0.1', '-', 'foo',
            '01/Jul/2000:00:00:00 +0000',
            utils.request_line('GET', '/foo', 'HTTP/1.0'),
            '200', '100')
        expected = collections.Counter(['foo'])

        self.collector.process_line(line)

        self.assertEqual(expected, self.collector.hist)

    def test_get_stats_normal(self):
        line = utils.log_line(
            '127.0.0.1', '-', 'foo',
            '01/Jul/2000:00:00:00 +0000',
            utils.request_line('GET', '/foo', 'HTTP/1.0'),
            '200', '100')
        expected = "1 most hit sections are: foo 1"

        self.collector.process_line(line)
        actual = self.collector.get_stats()

        self.assertEqual(expected, actual)

    def test_get_stats_padding(self):
        expected = "1 most hit sections are: - -"

        actual = self.collector.get_stats()

        self.assertEqual(expected, actual)
