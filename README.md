# dataBot
This is a discord bot (now using Nextcloud & ODS for open-source data management) designed to read/write to spreadsheets and analyze output.

## Directories

`local-data` -- stores the user's local copy of spreadsheet files. According to one tentative design, files fetched/created/modified by pyexcel-ods are temporarily stored in this directory. See that directory's README for details.

## Installation

### Dependencies

-   `pyexcel-ods` -- simply a library to interact with ODS spreadsheet files.
    you can install this with a simple `pip3 install`.

-   `nextcloud-API` -- A way to interface with the remote cloud storage (a candidate replacement for GoogleDocs). This is saved as a git submodule simply to keep versions consistent & up-to-date.
    -    you can install this by using the git submodule and typing `sudo python3 ./setup install`

### Configuration
Update the file secret.py with your custom credentials. For now, it takes the form of a simple python module that sets the following variables:
```
bot_token = 'bot-token-here'
update_channel_ID = channel-id-here 
host_username = '<@431491115775164418>'
```

## Design

One server will have its own spreadsheet; each user will be assigned one sheet.

## License

TBD

## Contributors

megumin00

chocorho

