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

from .base import BaseCollector


class SectionCollector(BaseCollector):
    """ Collector which keeps track of visits to particular sections of a site.

    Note, that this class implements non-overlapping hit rate calculation.
    """

    config_section = 'SectionCollector'
    message = "%d most hit sections are: %s"

    def __init__(self, config):
        super(SectionCollector, self).__init__(config)
        self.hist = collections.Counter()

    def process_line(self, line):
        """ Extracts section and counts how often it occurs."""
        l = line.request.path.split('/')[1]
        self.hist.update([l])

    def get_stats(self):
        """ Prepares statistics in ready to display format."""
        most_common = self.hist.most_common(self.statsize)
        stats = ["%s %d" % (x, y) for x, y in most_common]
        if len(stats) < self.statsize:
            stats.extend(["- -"]*(self.statsize - len(stats)))
        res = self.message % (self.statsize, ", ".join(stats))
        self.hist.clear()
        return res
