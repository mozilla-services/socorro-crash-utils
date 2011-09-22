This repository contains modules and tools for interacting with Socorro crash
data.

You will find some Python modules in socorro/.

In the root directory are the following scripts:

* parse_crashdata.py - Swiss army knife of the package. This reads crash data
  (either from daily CSV fails, a directory containing .json files, or stdin),
  filters the data (filters supplied by arguments), and then outputs whatever
  analysis you tell it to. Run with --help for complete usage info.

* download_crashdata.py - Convenience script for downloading the daily CSV
  crash dumps. It defaults to hit Mozilla's server and will download the
  last 30 days of crashes.

* download_dumps.py - Retrieves detailed dumps for individual crash UUIDs,
  which are specified on stdin. It simply opens an HTTP connection to
  Mozilla's socorro instance, fetches individual dumps, and writes them to
  a directory. These files can later be analyzed using parse_crashdata.py

##Example Workflow

Say you want to analyze crashes from the last week:

    # Download the past 7 days worth of crash dumps
    $ ./download_crashdata.py --days=7 ~/tmp/crashdata

Then, you want to filter the crashes based on a signature:

    # find all crashes where 'memcpy' appears in the signature
    # .gz files are automatically recognized!
    $ ./parse_crashdata.py --signature=memcpy ~/tmp/crashdata/*.gz

    # The above will print a list of crash UUIDs by default. You probably want
    # to do something useful with these UUIDs:
    $ ./parse_crashdata.py --signature=memcpy ~/tmp/crashdata/*.gz > ~/tmp/memcpy_ids

Now, let's dig deeper into crashes. First, we need to fetch the detailed crash
records for the crashes of interest:

    $ ./download_dumps.py ~/tmp/dumps < ~/tmp/memcpy_ids

Now, we perform some analysis of the detailed records:

    $ ./parse_crashdata.py --json-dir ~/tmp/dumps --print-frame-counts

