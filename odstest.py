#!/usr/bin/env python3
#
# Introductory test script to create a ODS file using the new API
#

import pyexcel_ods
import collections

# define local storage directory here
local_dir="local-data/"

entireSpreadsheet = collections.OrderedDict()
entireSpreadsheet.update({"Server1Sheet":[[1, 2, 3, 4, 5, 6], [1, 1, 2, 3, 5, 8]]})
entireSpreadsheet.update({"Server2Sheet":[["Username#pin", "message"],["chocorho#1337", "This is just a test message"]]})
#entireSpreadsheet.update({"Server2Sheet":[["", "This is just a test message"]]})
#entireSpreadsheet.update({"Server2Sheet":[["chocorho#1337", "This is just a test message"]]})

pyexcel_ods.save_data(local_dir+"testSheetFromPython.ods", entireSpreadsheet)

