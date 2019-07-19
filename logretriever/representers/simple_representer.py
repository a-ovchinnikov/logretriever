# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

from __future__ import print_function

import os

from .base import BaseRepresenter


class SimpleStatsRepresenter(BaseRepresenter):
    """ A very basic implementation of BaseRepresenter.

    All notices are dumped to terminal with minimal processing. A callback
    for alarms is provided for those collectors willing to inform about
    some activity in between regular display updates.
    """

    config_section = 'SimpleStatsRepresenter'

    def __init__(self, config, collectors):
        super(SimpleStatsRepresenter, self).__init__(config, collectors)
        for c in self.collectors:
            c.set_alarm_callback(self.alarm_callback)
        self.alarms = [''] * config.getint(self.config_section,
                                           'alarms_to_keep_track_of')

    def _clear_screen(self):
        os.system('cls||clear')

    def alarm_callback(self, alarm):
        if alarm not in self.alarms:
            self.alarms.pop(0)
            self.alarms.append(alarm)
            print(alarm)

    def show_stats(self):
        """ Simple statistics display routine."""
        self._clear_screen()
        print("\nMost recent alarms")
        print("-"*30)
        for alarm in self.alarms:
            print(alarm)
        print("\nStatistics over last %d seconds:" % self.stats_period)
        print("-"*30)
        for collector in self.collectors:
            print(collector.get_stats())
