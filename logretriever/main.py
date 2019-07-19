# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

import argparse
# NOTE(aovchinnikov): the try-block below ensures interoperability between
# Py2 and Py3.
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import datetime
import os
import signal
import sys
import time
import threading

import collectors as _collectors
import representers
import utils


sig_names = {2: 'SIGINT', 1: 'SIGHUP', 15: 'SIGTERM'}
just_continue = None

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="/etc/logretriever/config.cfg",
                    help="Path to configuration file with settings.")
parser.add_argument('--log_file', default=argparse.SUPPRESS,
                    help="Location of a log file to monitor.")
parser.add_argument('--check_interval', default=argparse.SUPPRESS,
                    help="How often to read updates from log file (in seconds)"
                    ".")
parser.add_argument('--statistics_interval', default=argparse.SUPPRESS,
                    help="Interval over which statistics should be collected.")
parser.add_argument('--alarm_interval', default=argparse.SUPPRESS,
                    help="A period over which alarm threshold should be"
                    " exceeded for an alarm to be generated.")
parser.add_argument('--alarm_threshold', default=argparse.SUPPRESS,
                    help="Number of events per second during alarm interval"
                    " which is considered an anomaly.")
parser.add_argument('--ignore_missing_bits', type=bool,
                    default=argparse.SUPPRESS,
                    help="Number of events per second during alarm interval"
                    " which is considered an anomaly.")

cliargs = parser.parse_args()
config = ConfigParser.SafeConfigParser()
sys.exit(1) if utils.file_has_problems(cliargs.config) else just_continue
config.read([cliargs.config])


def main():
    # Graceful interruption handler.
    def quit(signum, frame):
        """ Handler to catch interrupting signals.
        :param signum: Number of a caught signal.
        :param frame: Interpreter stack frame (not used, added to comply with
            standard).
        :return: None
        :side-effects: Sets global exit event.
        """
        sys.stderr.write("\nInterrupted by %s, exiting.\n" % sig_names[signum])
        sys.stderr.flush()
        exit.set()
    exit = threading.Event()
    for s in sig_names.values():
        signal.signal(getattr(signal, s), quit)

    # Configuration manipulation.
    utils.update_config_from_cli_arguments(config, cliargs)
    collectors = utils.load(config, 'collectors', _collectors)
    display = utils.load(config, 'representer', representers,
                         args=[collectors])[0]
    check_interval = config.getint('DEFAULT', 'check_interval')
    fname = config.get('DEFAULT', 'log_file')
    sys.exit(1) if utils.file_has_problems(fname) else just_continue

    # The processing itself.
    with open(fname, 'r') as f:
        f.seek(0, 2)  # Ignore historic data.
        display.show_stats()
        while True and not exit.is_set():
            start = datetime.datetime.now()
            data = list(filter(None, [utils.parse_line(x) for x in
                                      utils.get_fresh_events(f)]))
            for collector in collectors:
                for line in data:
                    collector.process_line(line)
            duration = (datetime.datetime.now() - start).total_seconds()
            to_wait = check_interval - duration
            if to_wait > 0:
                exit.wait(to_wait)
            else:
                sys.stderr.write("WARNING: too many events! Can not process"
                                 " them in %d second(s)!\n" % check_interval)
                sys.stderr.flush()
            display.tick()

if __name__ == '__main__':
    main()
