# coding=utf8
from __future__ import unicode_literals
from unittest import TestCase
from datetime import datetime

from httmock import all_requests, response, HTTMock


SERVICE_URL = 'http://example.org'


class Response(object):
    def __init__(self, key, status, content):
        self.key = key
        self.status = status
        self.content = content


RESPONSES = [
    Response(('/rest/items', 'get'), 200, {"Wo1JI_oZNyrfxV_t": {}}),
    Response(('/rest/items/Wo1JI_oZNyrfxV_t', 'delete'), 200, {}),
    Response(('/rest/items/Wo1JI_oZNyrfxV_t', 'get'), 200, {
        "id": "Wo1JI_oZNyrfxV_t",
        "createdBy": {
            "fullname": "Saquet",
            "id": "zhcQKsMR0A9SiC6x"
        },
        "modifiedBy": {
            "fullname": "Saquet",
            "id": "zhcQKsMR0A9SiC6x"
        },
        "createdDate": "2014-10-16T11:01:13 +0200",
        "modifiedDate": "2014-11-20T10:31:15 +0100",
        "versionDate": "2014-10-16T11:15:97 +0200",
        "status": "RELEASED",
        "version": 1,
        "discardComment": "",
        "visibility": "PUBLIC",
        "collectionId": "FKMxUpYdV9N2J4XG",
        "filename": "virr-image.tif",
        "mimetype": "application/octet-stream",
        "checksumMd5": "006a6dc402c6d84dc4c10d955599f57c",
        "webResolutionUrlUrl": "http://example.org/image.jpg",
        "thumbnailUrl": "http://example.org/image.jpg",
        "fileUrl": "http://example.org/image.jpg",
        "metadata": [
            {
                "position": 0,
                "value": {
                    "text": "title"
                },
                "statementUri": "http://imeji.org/terms/statement/xx9HntRF7GuFIJA",
                "typeUri": "http://imeji.org/terms/metadata#text",
                "labels": [
                    {
                        "language": "en",
                        "value": "titel"
                    }
                ]
            },
            {
                "position": 1,
                "value": {
                    "name": "Munich, Germany",
                    "longitude": 11.5819806,
                    "latitude": 48.1351253
                },
                "statementUri": "http://imeji.org/terms/statement/dCIHVzo4TWBD1bWc",
                "typeUri": "http://imeji.org/terms/metadata#geolocation",
                "labels": [
                    {
                        "language": "en",
                        "value": "goelocation"
                    }
                ]
            },
            {
                "position": 2,
                "value": {
                    "person": {
                        "position": 0,
                        "id": "sCooi0G_D8SW5__",
                        "familyName": "Saquet",
                        "givenName": "Bastien",
                        "completeName": "Saquet, Bastien",
                        "alternativeName": "",
                        "role": "author",
                        "identifiers": [
                            {
                                "type": "imeji",
                                "value": "http://pubman.mpdl.mpg.de/cone/persons"
                                         "/resource/persons96343"
                            }
                        ],
                        "organizations": [
                            {
                                "position": 0,
                                "id": "KHUV7faLBp9R5Zqm",
                                "name": "Innovations, MPDL, Max Planck Society",
                                "description": "",
                                "identifiers": [
                                    {
                                        "type": "imeji",
                                        "value": "escidoc:persistent1"
                                    }
                                ],
                                "city": "",
                                "country": ""
                            }
                        ]
                    }
                },
                "statementUri": "http://example.org/statement",
                "typeUri": "http://imeji.org/terms/metadata#conePerson",
                "labels": [
                    {
                        "language": "en",
                        "value": "Person"
                    }
                ]
            }
        ]
    }),
    Response(('/rest/items/Wo1JI_oZNyrfxV_t/content', 'get'), 200, b'test'),
    Response(('/rest/collections', 'get'), 200, {"FKMxUpYdV9N2J4XG": {}}),
    Response(('/rest/collections/FKMxUpYdV9N2J4XG', 'get'), 200, {
        "id": "FKMxUpYdV9N2J4XG",
        "createdBy": {
            "fullname": "Saquet",
            "id": "zhcQKsMR0A9SiC6x"
        },
        "modifiedBy": {
            "fullname": "admin",
            "id": "w7ZfmmC5LQR8KJIN"
        },
        "createdDate": "2014-10-09T13:01:25 +0200",
        "modifiedDate": "2014-11-19T14:50:21 +0100",
        "versionDate": "2014-10-16T11:15:44 +0200",
        "status": "RELEASED",
        "version": 1,
        "discardComment": "",
        "title": "Research Data",
        "description": "Test for research data",
        "contributors": [
            {
                "position": 0,
                "id": "Od6MTBSdXYPWYSU1",
                "familyName": "Saquet",
                "givenName": "Bastien",
                "completeName": "Saquet, Bastien",
                "alternativeName": "",
                "role": "author",
                "identifiers": [
                    {
                        "type": "imeji",
                        "value": "http://pubman.mpdl.mpg.de/cone/persons"
                                 "/resource/persons96343"
                    }
                ],
                "organizations": [
                    {
                        "position": 0,
                        "id": "94zMk2OtjJAWtXIH",
                        "name": "Innovations, MPDL, Max Planck Society",
                        "description": "",
                        "identifiers": [
                            {
                                "type": "imeji",
                                "value": "escidoc:persistent1"
                            }
                        ],
                        "city": "",
                        "country": ""
                    }
                ]
            },
            {
                "position": 0,
                "id": "4S34HiEj6qvvgTV1",
                "familyName": "Bulatovic",
                "givenName": "Natasa",
                "completeName": "Bulatovic, Natasa",
                "alternativeName": "",
                "role": "author",
                "identifiers": [
                    {
                        "type": "imeji",
                        "value": "http://pubman.mpdl.mpg.de/cone/persons"
                                 "/resource/persons96308"
                    }
                ],
                "organizations": [
                    {
                        "position": 0,
                        "id": "OSCfm3llkE3Foa4",
                        "name": "Innovations, MPDL, Max Planck Society",
                        "description": "",
                        "identifiers": [
                            {
                                "type": "imeji",
                                "value": "escidoc:persistent1"
                            }
                        ],
                        "city": "",
                        "country": ""
                    }
                ]
            }
        ],
        "profileId": "dhV6XK39_UPrItK5"
    }),
    Response(('/rest/profiles/dhV6XK39_UPrItK5', 'get'), 200, {
        "id": "dhV6XK39_UPrItK5",
        "createdBy": {
            "fullname": "Saquet, Bastien",
            "userId": "zhcQKsMR0A9SiC6x"
        },
        "modifiedBy": {
            "fullname": "Saquet, Bastien",
            "userId": "zhcQKsMR0A9SiC6x"
        },
        "createdDate": "2014-10-09T13:01:49 +0200",
        "modifiedDate": "2014-11-20T10:31:13 +0100",
        "versionDate": "2014-10-16T11:15:54 +0200",
        "status": "RELEASED",
        "version": 0,
        "discardComment": "",
        "title": "Research Data",
        "description": "Test for research data",
        "statements": [
            {
                "id": "xx9HntRF7GuFIJA",
                "pos": 0,
                "type": "http://imeji.org/terms/metadata#text",
                "labels": [
                    {
                        "value": "titel",
                        "lang": "en"
                    }
                ],
                "vocabulary": None,
                "literalConstraints": [],
                "minOccurs": "0",
                "maxOccurs": "1",
                "parentStatementId": None,
                "useInPreview": True
            },
        ]
    }),
]
RESPONSES = {r.key: r for r in RESPONSES}

RESPONSES[('/rest/collections', 'post')] = Response(
    ('/rest/collections', 'post'),
    201,
    RESPONSES[('/rest/collections/FKMxUpYdV9N2J4XG', 'get')].content)
RESPONSES[('/rest/items', 'post')] = Response(
    ('/rest/items', 'post'),
    201,
    RESPONSES[('/rest/items/Wo1JI_oZNyrfxV_t', 'get')].content)


@all_requests
def imeji(url, request):
    headers = {'content-type': 'application/json'}
    res = RESPONSES[(url.path, request.method.lower())]
    return response(res.status, res.content, headers, None, 5, request)


class ApiTest(TestCase):
    def setUp(self):
        from pyimeji.api import Imeji

        self.api = Imeji(service_url=SERVICE_URL)

    def test_collection(self):
        with HTTMock(imeji):
            collections = self.api.collections()
            self.assertIn('FKMxUpYdV9N2J4XG', collections)
            collection = self.api.collection(list(collections.keys())[0])
            self.assertEqual(collection.title, 'Research Data')
            collection.title = 'New title'
            self.assertIsInstance(collection.createdDate, datetime)
            self.assertEqual(collection.title, 'New title')
            collection.dumps()
            repr(collection)
            collection2 = self.api.create('collection', title='abc')
            collection2.add_item(referenceUrl='http://example.org/')
            assert collection2

    def test_item(self):
        with HTTMock(imeji):
            items = self.api.items()
            self.assertIn('Wo1JI_oZNyrfxV_t', items)
            item = self.api.item(list(items.keys())[0])
            self.assertEqual(item.filename, 'virr-image.tif')
            self.assertRaises(ValueError, self.api.item)
            self.assertRaises(AttributeError, getattr, item, 'abc')
            self.assertRaises(AttributeError, setattr, item, 'id', 'abc')
            self.assertEqual(item.content.text, 'test')
            item2 = self.api.create('item', collectionId='abc', file=__file__)
            assert item2
            item2.delete()
            self.api.delete(item)

    def test_profile(self):
        with HTTMock(imeji):
            profile = self.api.profile('dhV6XK39_UPrItK5')
            self.assertEqual(profile.title, 'Research Data')

    def test_cli(self):
        from pyimeji.cli import main
        from pyimeji.resource import Collection

        with HTTMock(imeji):
            res = main(
                ('--service=%s retrieve collection FKMxUpYdV9N2J4XG' % SERVICE_URL)
                .split())
            self.assertIsInstance(res, Collection)
