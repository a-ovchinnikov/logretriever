# (c) 2019 Alexey Ovchinnikov
#
# This is an illustrative work intended for demonstration purposes only.
# Any other use is discouraged.
#
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-NoDerivatives 4.0 International License.
# For full license agreement please see:
# http://creativecommons.org/licenses/by-nc-nd/4.0/

""" Handy helper functions for log processor."""

import collections
import datetime
import os
import re
import sys


request_line = collections.namedtuple('Request',
                                      ['method', 'path', 'protocol'])

log_line = collections.namedtuple('LogLine',
                                  ['ip', 'identifier', 'userid', 'date',
                                   'request', 'response_code', 'size'])

# NOTE(aovchinnikov): Proper parsing of date is a non-trivial task given that
# date could appear in different formats, time zones are not easily accounted
# for etc. Thus for now I will just store date as is. In the future it might
# make sense to have a family of classes capable to take care of different date
# formats and to select one basing on config value for date format.

ptr = re.compile('([(\d\.)]+) (.*?) (.*?) \[(.*?)\] "(.*?)" (\d+) (\d+)')


def parse_line(line):
    """ CLF line parser."""
    res = re.match(ptr, line)
    if res is None:
        return
    addr, uid, user, date, request, code, size = res.groups()
    request = request_line(*request.split())
    return log_line(addr, uid, user, date, request, code, size)


def get_fresh_events(f):
    """ Read a fresh batch of newline-separated strings from a file.

    :param f: File object to read fresh entries from.
    :return: A list of strings.
    """
    # NOTE(aovchinnikov): the logic below should work fine up to several
    # thousands new entries per second. I have not tested it with higher
    # loads so if faced with such rates use with care.
    pos = f.tell()
    # Make sure the file has not been truncated between reads:
    f.seek(0, 2)
    eof = f.tell()
    if eof >= pos:
        f.seek(pos)
    else:
        f.seek(0)
        pos = 0
    data = f.read()
    # Make sure there are no partial lines in the input:
    last_eol = data.rfind('\n')
    if last_eol != -1:  # There is something to return.
        f.seek(pos+last_eol+1)
        return data[:last_eol].split('\n')
    # No newlines in input means no new processable data thus far.
    return []


def load(config, option, from_where, args=None):
    """ A simple loader for helper classes.

    A loader loads classes basing on a comma-separated list contained in
    a configuration file. The loader is rather simplistic and relies on
    certain structure of a project.
    :param config: ConfigParser object initialized from a config file.
    :param option: option name with a list of classes to load.
    :param from_where: module from which to load these classes.
    :param args: Optional arguments to pass to all classes constructors.
    :return: list of configured objects.
    :raises: Does not raise anything, but by default stops execution when
    encounters an unknown class name.
    """
    # NOTE(aovchinnikov): since I use DIY loader I sacrifice some generality
    # and readability for simplicity. Thus it always returns a list of objects
    # no matter how many were actually created which complicates its usage a
    # bit.
    class_names = config.get('DEFAULT', option).replace(' ', '').split(',')
    out, args = [], [] if args is None else args
    for el in class_names:
        cls = getattr(from_where, el, None)
        if cls is None:
            msg = "No %(cls)s could be found in module %(mod)s" % {
                  'cls': el, 'mod': from_where.__name__}
            if config.getboolean('DEFAULT', 'ignore_missing_bits'):
                sys.stderr.write("WARNING: %s\n" % msg)
                sys.stderr.flush()
                continue
            else:
                # Since it is a configuration problem there is little reason to
                # raise an exception and to try to handle it.
                sys.stderr.write('ERROR: %s\n' % msg)
                sys.exit(1)
        out.append(cls(config, *args))
    return out


def file_has_problems(fname):
    """ Simple checker for file accessibility.

    :param fname: file name to check.
    :return: True if file is in some way inaccessible.
    """
    if not os.path.isfile(fname):
        sys.stderr.write("ERROR: File not found: %s\n" % fname)
        return True
    if not os.access(fname, os.R_OK):
        sys.stderr.write("ERROR: Permission denied: %s\n" % fname)
        return True
    return False


def update_config_from_cli_arguments(config, arguments):
    """ Overrides values loaded from DEFAULT section with CLI arguments.

    :param config: ConfigParser object to override.
    :param arguments: Namespace with override values.
    :return: None
    :side-effects: Modifies config object.
    """
    for dopt in config.defaults():
        if dopt in arguments:
            config.set('DEFAULT', dopt, getattr(arguments, dopt))
