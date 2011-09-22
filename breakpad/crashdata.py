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

import csv
import httplib

from datetime import datetime
from json import loads

# TODO make crash parsing more efficient. Currently it converts CSV to dict
# then to another dict. Lots of extra shuffling that can be eliminated.

class CrashDataParser(object):

    def __init__(self):
        pass

    def _handle_reader(self, reader):
        for row in reader:
            yield CrashData(csv_row_dict=row)

    def parse_handle(self, fh):
        reader = csv.DictReader(fh, delimiter='\t')
        return self._handle_reader(reader)

    def parse_file(self, path):
        with open(path, 'rb') as fh:
            reader = csv.DictReader(fh, delimiter='\t')
            return self._handle_reader(reader)

class CrashData(object):
    '''Represents a single crash report'''

    __slots__ = [
        'addons',
        'adu_count',
        'address',
        'addons_checked',
        'app_notes',
        'branch',
        'bugs',
        'build',
        'build_date',
        'completed_date',
        'cpu_info',
        'cpu_name',
        'crashed_thread',
        'crash_date',
        'date_processed',
        'distributor',
        'distributor_version',
        'duplicate_of',
        'flash_version',
        'hangid',
        'id',
        'install_age',
        'last_crash',
        'modules',
        'os_version',
        'os_name',
        'plugin_filename',
        'plugin_name',
        'plugin_version',
        'process_type',
        'processor_notes',
        'product',
        'release_channel',
        'reason',
        'signature',
        'stacks',
        'started_time',
        'success',
        'topmost_filenames',
        'truncated',
        'uptime',
        'user_comments',
        'uuid',
        'uuid_url',
        'version',
    ]

    def __init__(self, csv_row_dict=None, json=None):
        '''Construct a crash data instance.

        Crash data can be reconstructed from a number of sources.
        JSON is the most complete crash data.
        '''

        self.modules = []
        self.stacks = {}

        if json is not None:
            self.from_json(json)
        elif csv_row_dict is not None:
            self.from_csv_dict(csv_row_dict)

    def from_csv_dict(self, row):
        '''Creates a new instance from a parsed CSV row created by DictReader

        This will likely only be called from CrashDataParser.
        '''
        self.from_dict(row, full=False)


    def from_json(self, json):
        '''Populate data from a JSON-string

        The string should be the JSON representation of an object. This JSON
        blob likely comes from the crash-stats HTTP server.
        '''
        self.from_dict(loads(json), full=True)

    def from_dict(self, d, full=False):
        def string_to_datetime(v, full=False):
            fmt = '%Y%m%d%H%M'

            if full:
                i = v.find('.')
                if i != -1:
                    v = v[0:i]

                fmt = '%Y-%m-%d %H:%M:%S'

            return datetime.strptime(v, fmt)

        for k, v in d.iteritems():
            if k == '':
                continue
            elif k == 'addons':
                self.addons = v
            elif k == 'address':
                self.address = v
            elif k == 'adu_count':
                self.adu_count = v
            elif k == 'addons_checked':
                self.addons_checked = v
            elif k == 'app_notes':
                self.app_notes = v
            elif k == 'build':
                self.build = v
            elif k == 'build_date':
                self.build_date = string_to_datetime(v, full)
            elif k == 'branch':
                self.branch = v
            elif k == 'bug_list':
                self.bugs = [int(b) for b in v.split(',') if len(b) > 0]
            elif k == 'client_crash_date':
                self.crash_date = string_to_datetime(v, full)
            elif k == 'completeddatetime':
                self.completed_date = string_to_datetime(v, full)
            elif k == 'cpu_info':
                self.cpu_info = v.split(' | ')
            elif k == 'cpu_name':
                self.cpu_name = v
            elif k == 'crashedThread':
                # while thread IDs are typically integers, we can't assume
                self.crashed_thread = str(v)
            elif k == 'date_processed':
                self.date_processed = string_to_datetime(v, full)
            elif k == 'distributor':
                self.distributor = v
            elif k == 'distributor_version':
                self.distributor_version = v
            elif k == 'dump':
                # this is handled specially later
                pass
            elif k == 'duplicate_of':
                d = None
                if v != '\\N':
                    # TODO convert to UUID
                    d = v
                self.duplicate_of = d

            elif k == 'flash_version':
                self.flash_version = v
            elif k == 'hangid':
                self.hangid = v
            elif k == 'id':
                self.id = v
            elif k == 'install_age':
                self.install_age = int(v)
            elif k == 'last_crash':
                self.last_crash = v
            elif k == 'os_name':
                self.os_name = v
            elif k == 'os_version':
                self.os_version = v
            elif k == 'pluginFilename':
                self.plugin_filename = v
            elif k == 'pluginName':
                self.plugin_name = v
            elif k == 'pluginVersion':
                self.plugin_version = v
            elif k == 'process_type':
                self.process_type = v
            elif k == 'processType':
                self.process_type = v
            elif k == 'processor_notes':
                self.processor_notes = v
            elif k == 'product':
                self.product = v
            elif k == 'reason':
                self.reason = v
            elif k == 'release_channel':
                self.release_channel = v
            elif k == 'ReleaseChannel':
                self.release_channel = v
            elif k == 'signature':
                self.signature = v.split(' | ')
            elif k == 'startedDateTime':
                self.started_time = string_to_datetime(v, full)
            elif k == 'success':
                self.success = v
            elif k == 'topmost_filenames':
                self.topmost_filenames = v
            elif k == 'truncated':
                self.truncated = v
            elif k == 'URL (removed)':
                continue
            elif k == 'uptime_seconds':
                self.uptime = int(v)
            elif k == 'uptime':
                self.uptime = int(v)
            elif k == 'user_comments':
                self.user_comments = v
            elif k == 'uuid':
                self.uuid = v
            elif k == 'uuid_url':
                self.uuid_url = v

                i = v.find('/report/index/')

                if i != -1:
                    self.uuid = v[i + len('/report/index/'):]
            elif k == 'version':
                self.version = v
            elif k == 'Winsock_LSP':
                pass

            else:
                print 'UNHANDLED KEY: %s = %s' % ( k, v )

        if 'dump' in d:
            dump = d['dump']
            lines = dump.split('\n')

            # TODO do stuff with these
            os = lines[0]
            cpu = lines[1]
            crash = lines[2]

            i = 3
            mode = 0
            while i < len(lines):
                line = lines[i].strip()
                i += 1

                # module list
                if mode == 0:
                    if line[0:7] == 'Module|':
                        self.modules.append(line.split('|'))
                    elif len(line) == 0:
                        mode = 1
                    else:
                        raise Exception('Invalid dump format')
                # stacks
                elif mode == 1:
                    frame = line.split('|')
                    thread = frame[0]

                    frame[1] = int(frame[1])

                    if thread not in self.stacks:
                        self.stacks[thread] = [frame]
                    else:
                        self.stacks[thread].append(frame)

    def has_signature(self, s):
        '''Returns whether the current crash has the specified signature'''
        for sig in self.signature:
            if sig.find(s) != -1:
                return True

        return False

    def has_stacks(self):
        '''Returns whether we have stacks for the current crash'''
        return len(self.stacks) > 0

    def get_crashed_stack(self):
        '''Returns the stack for the crashed thread

        Returns an array of frames on success or None if stack not found.
        '''
        thread = self.crashed_thread

        if not thread or thread not in self.stacks:
            return None

        return self.stacks[thread]

class DumpFetcher(object):
    '''Utility class to fetch dumps from the server.'''

    def __init__(self, domain, is_secure=True):
        self.domain = domain
        self.is_secure = is_secure

    def fetch_dumps(self, ids):
        '''Fetch a set of dumps by ID'''

        def get_connection():
            conn = None
            if self.is_secure:
                conn = httplib.HTTPSConnection(self.domain, 443)
            else:
                conn = httplib.HTTPConnection(self.domain, 80)

            return conn

        conn = None

        for id in ids:
            if not conn:
                conn = get_connection()

            conn.request('GET', '/dumps/%s.jsonz' % id)
            response = conn.getresponse()

            if response.status != 200:
                # TODO don't print to stdout
                print 'UUID not fetched: %s %d' % ( id, response.status )
                conn = None
                continue

            yield (id, response.read())

