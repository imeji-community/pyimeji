
Command Line Interface
----------------------

*pyimeji*'s command line interface working against
the "imeji" open source software
for management of research data and its JSON-based REST API.

 .. seealso:: imeji Home  http://imeji.org
 .. seealso:: imeji Sources https://github.com/imeji-community/imeji
 .. seealso:: imeji REST API documentation https://github.com/imeji-community/imeji/wiki/A_Home-imeji-API-V1

In the following examples ``$`` denotes a shell prompt.
Successful execution of a command will return ``0`` as exit status.


Usage instructions
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ imeji --help
    imeji

    Usage:
      imeji create <what> <properties>
      imeji [options] retrieve <what> <id>
      imeji delete <what> <id>
      imeji -h | --help
      imeji --version

    Options:
      -h --help        Show this screen.
      --version        Show version.
      --service=<URL>  URL of the imeji service

Currently this program supports three subcommands, "create", "retrieve" and "delete".


create
~~~~~~

Successful creation of an imeji object will print the JSON serialization of this object
to ``stdout``:

.. code-block:: javascript

    imeji create collection 'title=PyImeji CLI Collection Test;description=Description of the PyImeji'
    {
    "contributors": [
        {
            "alternativeName": "",
            "completeName": "",
            "familyName": "none",
            "givenName": "",
            "id": "E344fe8nfk3CpHQm",
            "identifiers": [
                {
                    "type": "imeji",
                    "value": "E344fe8nfk3CpHQm"
                }
            ],
            "organizations": [
                {
                    "city": "",
                    "country": "",
                    "description": "",
                    "id": "eUYndEKw6JN5GCap",
                    "identifiers": [
                        {
                            "type": "imeji",
                            "value": "eUYndEKw6JN5GCap"
                        }
                    ],
                    "name": "none"
                }
            ],
            "role": "author"
        }
    ],
    "createdBy": {
        "fullname": "Bulatovic, Natasa",
        "userId": "w1Xwtwc3BDYkNuG"
    },
    "createdDate": "2016-06-15T10:04:15 +0200",
    "description": "Description of the PyImeji",
    "discardComment": "",
    "id": "6b_2hjzWJyYISqb",
    "modifiedBy": {
        "fullname": "Bulatovic, Natasa",
        "userId": "w1Xwtwc3BDYkNuG"
    },
    "modifiedDate": "2016-06-15T10:04:15 +0200",
    "profile": {
        "id": null,
        "method": null
    },
    "status": "PENDING",
    "title": "PyImeji CLI Collection Test",
    "version": 0,
    "versionDate": ""
}


retrieve
~~~~~~~~

Successful retrieval of an imeji object will print the JSON serialization of this object
to ``stdout``:

.. code-block:: javascript

    $ imeji retrieve item gg98g44qpXkB4XdH
    {
        "checksumMd5": "d41d8cd98f00b204e9800998ecf8427e",
        "collectionId": "IgCw438si5hRXC6n",
        "createdBy": {
            "fullname": "Forkel, Robert",
            "userId": "lZANcuLhG2E1ePL5"
        },
        "createdDate": "2015-01-22T09:05:49 +0100",
        "discardComment": "",
        "fileUrl": "...",
        "filename": "file",
        "id": "gg98g44qpXkB4XdH",
        "metadata": [],
        "mimetype": "application/octet-stream",
        "modifiedBy": {
            "fullname": "Forkel, Robert",
            "userId": "lZANcuLhG2E1ePL5"
        },
        "modifiedDate": "2015-01-22T09:05:50 +0100",
        "status": "RELEASED",
        "thumbnailUrl": "...",
        "version": 1,
        "versionDate": "2015-01-22T09:05:50 +0100",
        "visibility": "PUBLIC",
        "webResolutionUrlUrl": "..."
    }


delete
~~~~~~

.. code-block:: bash

    $ imeji delete item gg98g44qpXkB4XdH


Error handling
~~~~~~~~~~~~~~

Should a command fail, i.e. get an unexpected API response, the command will return ``-1``
and error information is logged as follows:

.. code-block:: bash

    $ imeji delete item gg98g44qpXkB4XdH
    ERROR:pyimeji.api:got HTTP 403, expected HTTP 204
    ERROR:pyimeji.api:{
        "error" : {
            "code" : "1403",
            "title" : "Forbidden",
            "message" : "authorization-failed-message",
            "exceptionReport" : "*** not allowed to delete ..."
        }
    }
