# coding=utf8
from __future__ import unicode_literals
from unittest import TestCase
from collections import namedtuple

from httmock import all_requests, response, HTTMock


SERVICE_URL = 'http://example.org'

Response = namedtuple('Response', 'key status content')

RESPONSES = [
    Response(('/collections/', 'get'), 200, {"cid": {}}),
    Response(('/collections/cid', 'get'), 200, {
        "title": "Test Title Updated",
        "versionOf": "",
        "uri": "xyz",
        "description": "Test Description Updated",
        "authors": [
            {
                "family_name": "Müller",
                "given_name": "Max",
                "affiliations": [
                    {
                        "organization": "Organization1"
                    },
                    {
                        "organization": "Organization2"
                    }
                ]
            },
            {
                "family_name": "SmithHYYYY",
                "given_name": "John",
                "affiliations": [
                    {
                        "organization": "Organization6"
                    }
                ]
            }
        ],
        "metadata_profiles": [
            {
                "uri": "some-uri"
            }
        ]
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
            collections = self.api.collections
            self.assertIn('cid', collections)
