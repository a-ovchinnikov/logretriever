# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

import datetime

from .base import BaseCollector


now = datetime.datetime.now


class SimpleCollector(BaseCollector):
    """ Simple collector which counts and alerts on total number of requests.

    In case the average number of requests exceeds preconfigured threshold
    an alert will be issued. When average request rate is back to normal
    another alert will be issued informing the user about that fact. Note,
    that being simple the collector uses sliding window to process data and
    thus is quite prone to issuing excessive amount of alerts when encountering
    certain traffic patterns. When facing this issue it is advised to use a
    slightly more sophisticated collector with forced cool-down between alerts.
    """

    config_section = 'SimpleCollector'
    stat_msg = "Hit rate: %d"
    lh_msg = "%(time)s: WARNING! High traffic: average %(hr)d hits per second."
    hl_msg = "%(time)s: INFO: Traffic is back to normal."

    def __init__(self, config):
        super(SimpleCollector, self).__init__(config)
        self.alarm_period = config.getint(self.config_section,
                                          'alarm_interval')
        self.alarm_threshold = config.getint(self.config_section,
                                             'alarm_threshold')
        self.rates_window = [0] * max(self.alarm_period, self.statsize)
        self.alarm_is_on = False
        self.window_total = 0
        self.events_count = 0

    def process_line(self, logline):
        self.events_count += 1

    def tick(self):
        self.window_total -= self.rates_window.pop(0)
        self.window_total += self.events_count
        self.rates_window.append(self.events_count)
        self.events_count = 0
        self.alarm()

    def alarm(self):
        hit_rate = int(float(self.window_total)/self.alarm_period)
        if hit_rate >= self.alarm_threshold and not self.alarm_is_on:
            self.alarm_is_on = True
            self.alarm_callback(self.lh_msg % {'hr': hit_rate, 'time': now()})
        elif hit_rate < self.alarm_threshold and self.alarm_is_on:
            self.alarm_is_on = False
            self.alarm_callback(self.hl_msg % {'time': now()})

    def get_stats(self):
        return self.stat_msg % (
            sum(self.rates_window[-self.statsize:])/self.statsize)
