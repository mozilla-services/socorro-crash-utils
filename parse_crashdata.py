#!/usr/bin/python

# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is Breakpad Tools
#
# The Initial Developer of the Original Code is Mozilla Foundation.
#
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#  Gregory Szorc <gps@mozilla.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisiwons above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

# This script reads bulk crash dumps (as CSV) from stdin and performs
# filtering and prints out info.
#
# It iterates over all crashes from stdin. Then, it filters the crashes based
# on arguments. If a crash passes the filter, it moves on to the output stage.
# By default, it prints crash UUIDs. If a --print-* argument is defined, it
# skips printing UUIDs and will instead print the thing(s) it was told to.
#
# Alternatively, crashes can be read in from a directory containing .json
# files. These JSON files represent a superset of the crash data available
# from the daily crash CSV files. These JSON files were likely obtained from
# the crash server.

from socorro.crashdata import CrashDataParser, CrashData
from optparse import OptionParser
from os import listdir
from os.path import exists, join
from sys import stdin

import gzip

op = OptionParser()
op.add_option('--signature', '-s', dest='signature', default=None,
              help='Filter crashes by those containing this string in signature')
op.add_option('--json-dir', dest='json_dir', default=None,
              help='Directory containing .json files for raw crash dumps to read')
op.add_option('--print-versions', dest='print_versions', default=False,
              action='store_true',
              help='Print a summary of version counts')
op.add_option('--print-frame-counts', dest='print_frame_counts', default=False,
              action='store_true',
              help='Print a count of symols seen in crashed stacks')
op.add_option('--print-frame-position-counts', dest='print_frame_position_counts',
              default=False, action='store_true',
              help='Like --print-frame-counts but groups frames by stack position')

(options, args) = op.parse_args()

read_files = len(args) > 0
read_json = options.json_dir
print_uuids = True

collect_frames = False

if options.print_versions:
    print_uuids = False

if options.print_frame_counts or options.print_frame_position_counts:
    print_uuids = False
    collect_frames = True

version_counts = {}
frame_counts = {} # key is tuple so we track different areas of occurence
frame_symbol_counts = {} # key is symbol name

def handle_crash(row):
    # filter stage
    relevant = True

    if options.signature is not None:
        if not row.has_signature(options.signature):
            relevant = False

    if not relevant:
        return

    # data collection
    version = row.version
    if version not in version_counts:
        version_counts[version] = 1
    else:
        version_counts[version] += 1

    if collect_frames:
        stack = row.get_crashed_stack()

        if stack:
            for frame in stack:
                # TODO need better API for stacks/frames
                key = (frame[1], frame[2], frame[3])

                if key in frame_counts:
                    frame_counts[key] += 1
                else:
                    frame_counts[key] = 1

                if frame[3] in frame_symbol_counts:
                    frame_symbol_counts[frame[3]] += 1
                else:
                    frame_symbol_counts[frame[3]] = 1

    # individual printing
    if print_uuids:
        print row.uuid

parser = CrashDataParser()
if read_json:
    for p in listdir(read_json):
        if p[-5:] != '.json':
            continue

        filename = join(read_json, p)
        with open(filename, 'rb') as fh:
            crash = CrashData(json=fh.read())

            handle_crash(crash)

elif not read_files:
    for row in parser.parse_handle(stdin):
        handle_crash(row)
else:
    for filename in args:
        if not exists(filename):
            print 'Specified file does not exist: %s' % filename
            continue

        # automagically perform gzip uncompression
        if filename[-3:] == '.gz':
            gz = gzip.open(filename, 'rb')
            for row in parser.parse_handle(gz):
                handle_crash(row)

        else:
            for row in parser.parse_file(filename):
                handle_crash(row)

if options.print_versions:
    keys = version_counts.keys()
    keys.sort()

    for k in keys:
        print '%d\t%s' % ( version_counts[k], k )

if options.print_frame_counts:
    for k, v in frame_symbol_counts.iteritems():
        print '%d\t%s' % ( v, k )

if options.print_frame_position_counts:
    for k, v in frame_counts.iteritems():
        print '%d\t%d\t%s' % ( v, k[0], k[2] )
