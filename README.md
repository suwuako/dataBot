# dataBot
discord bot ~~using gspread~~ to read/write to spreadsheet and analyze output

## Branch purpose

Port the project to Nextcloud and ODS spreadsheets, in order to make the system more open-source and less dependent on Google services.

## Dependencies

-   `pyexcel-ods` -- simply a library to interact with ODS spreadsheet files.

-   `nextcloud-API` -- A way to interface with the remote cloud storage (a candidate replacement for GoogleDocs). This is saved as a git submodule simply to keep versions consistent & up-to-date.

## Directories

`local-data` -- stores the user's local copy of spreadsheet files. According to one tentative design, files fetched/created/modified by pyexcel-ods are temporarily stored in this directory. See that directory's README for details.

## License

TBD

## Contributors

megumin00

chocorho

