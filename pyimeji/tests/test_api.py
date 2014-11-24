# coding=utf8
from __future__ import unicode_literals
from unittest import TestCase
from collections import namedtuple

from httmock import all_requests, response, HTTMock


SERVICE_URL = 'http://example.org'

Response = namedtuple('Response', 'key status content')

RESPONSES = [
    Response(('/rest/collections/', 'get'), 200, {"FKMxUpYdV9N2J4XG": {}}),
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
        "createdDate": "2014-10-09T13:01:254 +0200",
        "modifiedDate": "2014-11-19T14:50:218 +0100",
        "versionDate": "2014-10-16T11:15:960 +0200",
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
                        "value": "http://pubman.mpdl.mpg.de/cone/persons/resource/persons96343"
                    }
                ],
                "organizations": [
                    {
                        "position": 0,
                        "id": "94zMk2OtjJAWtXIH",
                        "name": "Innovations, Max Planck Digital Library, Max Planck Society",
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
                        "value": "http://pubman.mpdl.mpg.de/cone/persons/resource/persons96308"
                    }
                ],
                "organizations": [
                    {
                        "position": 0,
                        "id": "OSCfm3llkE3Foa4",
                        "name": "Innovations, Max Planck Digital Library, Max Planck Society",
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
    })
]
RESPONSES = {r.key: r for r in RESPONSES}


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
            self.assertEqual(collection.title, 'New title')
            collection.dumps()
