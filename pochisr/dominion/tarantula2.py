#!/usr/bin/env python2

from __future__ import division, unicode_literals

import errno
import itertools
import os
import shlex
import sys
from collections import namedtuple
from itertools import izip
from math import log
from subprocess import Popen
from sys import stderr, stdout


SUSP_WIDTH = 8

USAGE_TEXT = """\
Usage: {} SOURCES GCDAS MINSEED MAXSEED
  SOURCES:  a colon-separated list of source files to analyze
    GCDAS:  a colon-separated list of gcda files that correspond to the
                source files
  MINSEED:  the minumum seed to use
  MAXSEED:  the maximum seed to use
"""


class TFile(object):
    __slots__ = ('line_count', 'lines')

    def __init__(self, line_count=0):
        self.line_count = line_count
        self.lines = [TLine() for i in xrange(line_count)]


class TLine(object):
    __slots__ = ('p', 'f', 'tp', 'tf')

    def __init__(self):
        self.p = self.f = self.tp = self.tf = 0

    def get_susp(self, pass_count, fail_count):
        if self.p + self.f == 0:
            return 0.0

        px = self.p / pass_count if pass_count > 0 else 0.0
        fx = self.f / fail_count if fail_count > 0 else 0.0
        tpx = self.tp / pass_count if pass_count > 0 else 0.0
        tfx = self.tf / fail_count if fail_count > 0 else 0.0

        r = tpx / (tpx + tfx)
        a = fx / (px + fx)
        c = px / (px + fx)
        try:
            return (a - (4 * px * fx) / (px + fx) ** 2 + 1) / 2
        except ZeroDivisionError:
            return 0.0


def main(sources, gcdas, minseed, maxseed):
    def run_and_analyze(*cmd):
        for gcda in gcdas:
            try:
                os.remove(gcda)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

        pass_ = int(0 == Popen(cmd, stdout=devnull).wait())

        if (Popen(['gcov'] + sources, stdout=devnull, stderr=devnull).wait()
                != 0):
            stderr.write('gcov failed\n')
            exit(1)

        for source in sources:
            try:
                with open(source + '.gcov') as f:
                    lines = iter(f)
                    for line in lines:
                        line = line.lstrip(' -:')
                        if line[0] != '0':
                            break

                    for i in itertools.count():  # First line is index 0.
                        count = line[:line.find(':')]
                        if count not in ('-', '#####'):
                            count = int(count)
                            susp[source].lines[i].p += pass_ * count
                            susp[source].lines[i].f += (1 - pass_) * count
                            susp[source].lines[i].tp += pass_
                            susp[source].lines[i].tf += 1 - pass_
                        line = next(f, None)
                        if line is None:
                            break
                        line = line.lstrip()
            except IOError as e:
                if e.errno != errno.ENOENT:
                    raise
                # Oh well.

        return pass_

    pass_count = 0
    fail_count = 0
    susp = {}  # suspiciousness

    for source in sources:
        line_count = 0
        with open(source) as f:
            while True:
                chunk = f.read(4096)
                if chunk == '':
                    break
                line_count += chunk.count('\n')
        susp[source] = TFile(line_count=line_count)

    for seed in xrange(minseed, maxseed + 1):
        pass_ = run_and_analyze('./testdominion', unicode(seed), '80000')
        pass_count += pass_
        fail_count += 1 - pass_

    for source in sources:
        line_digit_count = int(log(susp[source].line_count, 10)) + 1
        line_num_format = '  {{:{}}}:  '.format(line_digit_count)
        with open(source + '.tla', 'w') as t, open(source) as s:
            i = 0  # First line is number 1.
            for line, sline in izip(susp[source].lines, s):
                i += 1
                line_susp = int(
                    line.get_susp(pass_count, fail_count)
                    * SUSP_WIDTH)

                t.write(
                    ' ' * (SUSP_WIDTH - line_susp)
                    + '#' * line_susp
                    + line_num_format.format(i) + sline)


if __name__ == '__main__':
    global devnull
    devnull = open(os.devnull, 'wb')

    if len(sys.argv) != 5:
        stdout.write(USAGE_TEXT.format(sys.argv[0]))
        exit(2)

    main(
        sys.argv[1].split(':'), sys.argv[2].split(':'), int(sys.argv[3]),
        int(sys.argv[4]))
