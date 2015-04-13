# coding=utf8
from __future__ import unicode_literals
from unittest import TestCase
from datetime import datetime
import os

from httmock import all_requests, response, HTTMock

from pyimeji.util import pkg_path, jsonload, jsondumps


SERVICE_URL = 'http://example.org'


RESOURCES = {
    name: jsonload(pkg_path('tests', 'resources', '%s.json' % name))
    for name in ['item', 'collection', 'album', 'profile']}


class Response(object):
    def __init__(self, key, status, content):
        self.key = key
        self.status = status
        self.content = content


RESPONSES = {}

for path, method, status, content in [
    ('items', 'get', 200, jsondumps([{"id": "Wo1JI_oZNyrfxV_t"}])),
    ('items', 'post', 201, RESOURCES['item']),
    ('items/Wo1JI_oZNyrfxV_t', 'delete', 204, {}),
    ('items/Wo1JI_oZNyrfxV_t', 'get', 200, RESOURCES['item']),
    ('items/Wo1JI_oZNyrfxV_t', 'put', 200, RESOURCES['item']),

    ('collections', 'get', 200, jsondumps([{"id": "FKMxUpYdV9N2J4XG"}])),
    ('collections', 'post', 201, RESOURCES['collection']),
    ('collections/FKMxUpYdV9N2J4XG/release', 'put', 200, {}),
    ('collections/FKMxUpYdV9N2J4XG', 'delete', 204, {}),
    ('collections/FKMxUpYdV9N2J4XG', 'get', 200, RESOURCES['collection']),
    ('collections/FKMxUpYdV9N2J4XG/items', 'get', 200, jsondumps([RESOURCES['item']])),

    ('profiles/dhV6XK39_UPrItK5', 'get', 200, RESOURCES['profile']),

    ('albums', 'get', 200, jsondumps([{"id": "MAlOuZ4Y9iDR_"}])),
    ('albums', 'post', 201, RESOURCES['album']),
    ('albums/MAlOuZ4Y9iDR_/release', 'put', 200, {}),
    ('albums/MAlOuZ4Y9iDR_/discard', 'put', 200, {}),
    ('albums/MAlOuZ4Y9iDR_', 'delete', 204, {}),
    ('albums/MAlOuZ4Y9iDR_', 'get', 200, RESOURCES['album']),
    ('albums/MAlOuZ4Y9iDR_/members', 'get', 200, jsondumps([RESOURCES['item']])),
    ('albums/MAlOuZ4Y9iDR_/members/link', 'put', 200, {}),
    ('albums/MAlOuZ4Y9iDR_/members/unlink', 'put', 204, {}),
]:
    r = Response(('/rest/' + path, method), status, content)
    RESPONSES[r.key] = r


@all_requests
def imeji(url, request):
    headers = {'content-type': 'application/json'}
    res = RESPONSES[(url.path, request.method.lower())]
    return response(res.status, res.content, headers, None, 5, request)


class ApiTest(TestCase):
    def setUp(self):
        from pyimeji.api import Imeji

        self.api = Imeji(service_url=SERVICE_URL)

    def test_album(self):
        with HTTMock(imeji):
            albums = self.api.albums()
            album = self.api.album(list(albums.keys())[0])
            assert 'Wo1JI_oZNyrfxV_t' in album.members()
            assert album.id in album.member('Wo1JI_oZNyrfxV_t')._path()
            album.release()
            album.link()
            album.unlink()
            album.discard('test')

    def test_collection(self):
        with HTTMock(imeji):
            collections = self.api.collections()
            self.assertIn('FKMxUpYdV9N2J4XG', collections)
            collection = self.api.collection(list(collections.keys())[0])
            assert 'Wo1JI_oZNyrfxV_t' in collection.items()
            self.assertEqual(collection.title, 'Research Data')
            collection.title = 'New title'
            self.assertIsInstance(collection.createdDate, datetime)
            self.assertEqual(collection.title, 'New title')
            collection.dumps()
            repr(collection)
            collection2 = self.api.create(
                'collection', title='abc', profile='dhV6XK39_UPrItK5')
            collection2.add_item(referenceUrl='http://example.org/')
            assert collection2
            collection.release()
            collection2.delete()
            collection3 = self.api.create(
                'collection',
                title='cde',
                profile=self.api.profile('dhV6XK39_UPrItK5'))

    def test_item(self):
        with HTTMock(imeji):
            self.api.create('item', _file=__file__)
            items = self.api.items()
            self.assertIn('Wo1JI_oZNyrfxV_t', items)
            item = self.api.item(list(items.keys())[0])
            self.assertEqual(item.filename, 'virr-image.tif')
            self.assertRaises(ValueError, self.api.item)
            self.assertRaises(AttributeError, getattr, item, 'abc')
            self.assertRaises(AttributeError, setattr, item, 'id', 'abc')
            item2 = self.api.create('item', collectionId='abc', file=__file__)
            assert item2
            item2.metadata = os.path.join(os.path.dirname(__file__), 'test.json')
            self.api.update(item2, filename='name.png')
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
