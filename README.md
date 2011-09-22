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
