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


class UserCollector(BaseCollector):
    """ Collector which keeps track of the most active user.

    Note, that this class implements non-overlapping access score.
    """

    config_section = 'UserCollector'
    message = "Most active user: %s"

    def __init__(self, config):
        super(UserCollector, self).__init__(config)
        self.hist = collections.Counter()

    def process_line(self, line):
        self.hist.update([line.userid])

    def get_stats(self):
        most_common = self.hist.most_common(1)
        username = most_common[0][0] if most_common else '---'
        res = self.message % username
        self.hist.clear()
        return res
