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

# This script downloads all the available crash data from Mozilla's servers.

from datetime import date, timedelta
from optparse import OptionParser
from os.path import exists, join

import urllib2

op = OptionParser()
op.add_option('--base-uri', dest='uri', default='https://crash-analysis.mozilla.com/crash_analysis/')
op.add_option('--days', '-d', dest='days', default=30, type='int',
              help='The number of days to fetch')

(options, args) = op.parse_args()

if len(args) != 1:
    print 'Must specify output directory as argument'
    exit(1)

outdir = args[0]
today = date.today()

for i in range(1, options.days):
    d = today - timedelta(i)
    ds = d.strftime('%Y%m%d')

    uri = options.uri + ds + '/' + ds + '-pub-crashdata.csv.gz'
    filename = join(outdir, ds + '-pub-crashdata.csv.gz')

    if exists(filename):
        print 'Destination filename exists. Skipping: %s' % filename
        continue

    print 'Downloading %s to %s' % ( uri, filename )
    url = urllib2.urlopen(uri)
    with open(filename, 'wb') as fh:
        fh.write(url.read())

