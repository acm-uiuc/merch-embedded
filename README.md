# Merch Embedded

[![Join the chat at https://acm-uiuc.slack.com/messages/C6XD34KTM](https://img.shields.io/badge/slack-merch-724D71.svg)](https://acm-uiuc.slack.com/messages/C6XD34KTM)



This repository contains all of the code related to controlling the underlying merch hardware (the vending machine).
Merch runs an embedded webserver that can be accessed at merch.acm.illinois.edu.

## API

Requests to the device must contain a valid token in the Authorization Header for a request to be processed.
As of now the only token will be given solely to the groot merch service, so if you wish to make merch requests go through groot.


### Vend a location

To vend a list of items, POST a request to `/vend`.
The request is of the form
```json
{
    "transaction_id": 1,
    "items": ["A1", "B2", "C3"]
}
```

The machine will respond with
```json
{
    "transaction_id": 1,
    "items": [
        {"location": "A1", "error": null},
        {"location": "B2", "error": "some sort of error"},
        {"location": "C3", "error": null},

    ]
}
```

The errors that can take place while vending are currently:
* `"Invalid location"`


## Some related datasheets

[http://bajavending.com/Manual-de-Operacion-BevMax.pdf](http://bajavending.com/Manual-de-Operacion-BevMax.pdf)
* Has the right picture of the main controller board, no programming information though


[The LCD datasheet](https://media.digikey.com/pdf/Data%20Sheets/Noritake%20PDFs/GU140X16G-7003.pdf)


[LCD Code Library](https://www.noritake-elec.com/support/design-resources/code-libraries/code-library#gu7000)
has some useful info about what commands are sent

[LCD Command List](https://www.noritake-elec.com/support/design-resources/support-guide/gu-7000-command-description)

## License

This project is licensed under the University of Illinois/NCSA Open Source License. For a full copy of this license take a look at the LICENSE file.

When contributing new files to this project, preappend the following header to the file as a comment:

```
Copyright © 2017, ACM@UIUC

This file is part of the Merch Project.

The Merch Project is open source software, released under the University of Illinois/NCSA Open Source License.
You should have received a copy of this license in a file with the distribution.
```
