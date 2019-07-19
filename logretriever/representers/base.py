# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

""" Base class for representers to be based on."""

import abc
import os


class BaseRepresenter(object):
    """ Base class for all data representing classes.

    The purpose of a Representer is to display data collected by collectors in
    appropriate format. Note, that BaseRepresenter is not supposed to be
    instantiated directly.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, config, collectors):
        """ Basic init.

        :param config: initialized ConfigParser object.
        :param collectors: a list of collector objects.
        """
        super(BaseRepresenter, self).__init__()
        self.count = 0
        self.collectors = collectors
        self.stats_period = config.getint(self.config_section,
                                          'statistics_interval')

    def tick(self):
        """ Process clock pulses.

        React to clock pulses by keeping track of time, propagating clock
        pulses to collectors and taking action when time defined in config
        comes.
        """

        self.count += 1
        if self.count == self.stats_period:
            self.count = 0
            self.show_stats()
        for c in self.collectors:
            c.tick()

    @abc.abstractmethod
    def alarm_callback(self, alarm):
        """ A handle used by collectors to inform about an alarm (if any)."""

    @abc.abstractmethod
    def show_stats():
        """ Statistics will be displayed by this method.

        Must be implemented by concrete classes responsible for statistics
        representation.
        """
