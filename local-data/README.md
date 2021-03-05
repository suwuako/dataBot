# The local-data directory

A directory to store local copies of the spreadsheets from the Nextcloud server, if enabled.

A `.gitignore` has been added, in an effort to make sure a clients' spreadsheets (which could conceivably contain private or sensitive information) don't ever get committed to this repository.

An alternative to storing files locally is using temporary files, which turns out to be implemented not only as the [mktemp GNU coreutil](http://www.gnu.org/software/coreutils/manual/coreutils.html#mktemp-invocation) but also as [tempfile python library](https://docs.python.org/3/library/tempfile.html), which is likely better suited to our codebase. Testing on this method is necessary and has not begun; but it would theoretically be a good way to make file modification transparent to the user.

