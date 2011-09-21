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

from breakpad.crashdata import CrashDataParser
from optparse import OptionParser
from sys import stdin

op = OptionParser()
op.add_option('--signature', '-s', dest='signature', default=None,
              help='Filter crashes by those containing this string in signature')
op.add_option('--print-versions', dest='print_versions', default=False,
              action='store_true',
              help='Print a summary of version counts')

(options, args) = op.parse_args()

print_uuids = True

if options.print_versions:
    print_uuids = False

version_counts = {}

parser = CrashDataParser()
for row in parser.parse_handle(stdin):
    # filter stage
    relevant = True

    if options.signature is not None:
        if not row.has_signature(options.signature):
            relevant = False

    if not relevant:
        continue

    # data collection
    version = row.version
    if version not in version_counts:
        version_counts[version] = 1
    else:
        version_counts[version] += 1

    # individual printing
    if print_uuids:
        print row.uuid

if options.print_versions:
    keys = version_counts.keys()
    keys.sort()

    for k in keys:
        print '%s\t%s' % ( k, version_counts[k] )

