# dataBot
discord bot ~~using gspread~~ to read/write to spreadsheet and analyze output

## This branch

The purpose of this branch is to port the project to Nextcloud and ODS spreadsheets, in order to make the system more open-source and less dependent on Google services.

The new expected dependencies include [pyexcel-ods](https://github.com/pyexcel/pyexcel-ods) and [nextcloud-api](https://github.com/EnterpriseyIntranet/nextcloud-API).


## Directories

`local-data` -- stores the user's local copy of spreadsheet files. For example, files created/modified by pyexcel-ods are located in this directory.

`Nextcloud-API` -- a git submodule, simply to keep versions consistent & up-to-date.

