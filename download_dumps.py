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

# This script reads crash UUIDs from stdin and fetches the raw dumps from the
# crash server.

from os.path import exists, join
from sys import argv, stdin
from socorro.crashdata import DumpFetcher

if len(argv) != 2:
    print 'Usage: ./download_dumps.py /path/to/output/directory < file_of_uuids'
    exit(1)

outdir = argv[1]
if not exists(outdir):
    print 'Output directory does not exist: %s' % outdir
    exit(1)

fetcher = DumpFetcher('crash-stats.mozilla.com', True)

ids = []
for line in stdin:
    id = line.strip()
    filename = join(outdir, '%s.json' % id)
    if exists(filename):
        print 'Skipping %s because it exists: %s' % ( id, filename )
        continue

    ids.append(id)

for (id, jsonz) in fetcher.fetch_dumps(ids):
    filename = join(outdir, '%s.json' % id)

    with open(filename, 'wb') as fh:
        fh.write(jsonz)

    print 'Wrote %s to %s' % ( id, filename )
