# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

""" A tool to generate sample logs"""
import argparse
import datetime
import random
import signal
import sys
import threading
import time


# Dummy values.
addresses = ('127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4',)
names = ('jamest', 'jannet', 'jennie', 'johndr', 'joshua', 'julia2')
methods = ('GET', 'PUT', 'POST', 'HEAD')
site_structure = (
    ('foo', ('spam', 'eggs')),
    ('bar', ('quux', 'meep')),
    ('baz', ('flob', 'acme')),
    ('qux', ('frob', 'yolo')),
)
protocol = 'HTTP/1.0'
responses = ('200', '403', '404', '503')
size_range = (15, 5000)


#rs = random.choice
exit = threading.Event()
signal_names = {2: 'SIGINT', 1: 'SIGHUP', 15: 'SIGTERM'}


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('--rate', type=int, default=5,
                    help="How many messages to generate per second")
parser.add_argument('--seed', type=int, default=argparse.SUPPRESS,
                    help="Seed value for random numbers generator for"
                         " reproducible random sequences. No seeding is done"
                         " by default.")
parser.add_argument('--number', type=int, default=argparse.SUPPRESS,
                    help="Number of log lines to generate. Defaults to"
                         " infinity.")
args = parser.parse_args()


def generate_request():
    """ Generates a user request line for CLF"""
    section = random.choice(site_structure)
    path = '/'.join(['', section[0], random.choice(section[1])])
    return '"%s"' % ' '.join([random.choice(methods), path, protocol])


def generate_entry():
    """ Generates fake CLF line for testing purposes"""

    # NOTE(aovchinnikov): datetime.datetime.now() returns local time and knows
    # nothing about timezones. To keep things simple I have hardcoded timezone.
    # pytz could be used to extend datetime if such need ever arises in testing
    # context. For the same reason date is always now.
    d = datetime.datetime.now().strftime('[%d/%b/%Y:%H:%M:%S +0000]')

    return ' '.join([random.choice(addresses), '-', random.choice(names), d,
                     generate_request(), random.choice(responses),
                     str(random.randint(*size_range))])


def quit(signum, frame):
    """ Handler to catch interrupting signals."""
    sys.stderr.write("\nInterrupted by %s, exiting.\n" % signal_names[signum])
    sys.stderr.flush()
    exit.set()


def main():
    subtrahend = 1 if 'number' in args else 0
    generate_times = args.number if 'number' in args else 1
    if 'seed' in args:
        random.seed(args.seed)
    while generate_times and not exit.is_set():
        entry = generate_entry()
        sys.stdout.write("%s\n" % entry)
        sys.stdout.flush()
        generate_times -= subtrahend
        # NOTE(aovchinnikov): threading.Event() is used here to provide for
        # graceful interruption of inactive loops. The same could be done with
        # time.sleep() with a few less lines of code, but apparently it is
        # impossible to interrupt sleeping gracefully.
        exit.wait(1./(random.randint(1, args.rate)))


if __name__ == "__main__":
    for s in signal_names.values():
        signal.signal(getattr(signal, s), quit)
    main()
