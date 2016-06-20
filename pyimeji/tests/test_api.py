# coding=utf8
from __future__ import unicode_literals

import os
from datetime import datetime
from unittest import TestCase

from httmock import all_requests, response, HTTMock
from nose.tools import *

from pyimeji.util import pkg_path, jsonload, jsondumps

SERVICE_URL = 'http://example.org'

RESOURCES = {
    name: jsonload(pkg_path('tests', 'resources', '%s.json' % name))
    for name in ['item', 'collection', 'album', 'profile', 'item_template_collection', 'item_template_profile', 'collections']}


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
    ('collections', 'get', 200, RESOURCES['collections']),
    ('collections', 'post', 201, RESOURCES['collection']),
    ('collections/FKMxUpYdV9N2J4XG', 'put', 200, RESOURCES['collection']),
    ('collections/FKMxUpYdV9N2J4XG/release', 'put', 200, {}),
    ('collections/FKMxUpYdV9N2J4XG', 'delete', 204, {}),
    ('collections/FKMxUpYdV9N2J4XG', 'get', 200, RESOURCES['collection']),
    ('collections/FKMxUpYdV9N2J4XG?q=Test&offset=0&size=1', 'get', 200, RESOURCES['collections']),
    ('collections/FKMxUpYdV9N2J4XG/items', 'get', 200, jsondumps([RESOURCES['item']])),
    ('collections/FKMxUpYdV9N2J4XG/items/template', 'get', 200, RESOURCES['item_template_collection']),
    ('profiles/dhV6XK39_UPrItK5', 'get', 200, RESOURCES['profile']),
    ('profiles', 'post', 201, RESOURCES['profile']),
    ('profiles/dhV6XK39_UPrItK5/template', 'get', 200, RESOURCES['item_template_profile']),
    ('profiles/dhV6XK39_UPrItK5', 'delete', 204, {}),

    ('albums', 'get', 200, jsondumps([{"id": "MAlOuZ4Y9iDR_"}])),
    ('albums', 'post', 201, RESOURCES['album']),
    ('albums/MAlOuZ4Y9iDR_/release', 'put', 200, {}),
    ('albums/MAlOuZ4Y9iDR_/discard', 'put', 200, {}),
    ('albums/MAlOuZ4Y9iDR_', 'delete', 204, {}),
    ('albums/MAlOuZ4Y9iDR_', 'get', 200, RESOURCES['album']),
    ('albums/MAlOuZ4Y9iDR_/items', 'get', 200, jsondumps([RESOURCES['item']])),
    ('albums/MAlOuZ4Y9iDR_/members/link', 'put', 200, {}),
    ('albums/MAlOuZ4Y9iDR_/members/unlink', 'put', 204, {}),
    ('/', 'head', 200, {})
]:
    r = Response(('/rest/' + path if method != "head" else path, method), status, content)
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
            if not self.api.service_mode_private:
                album.release()
                album = self.api.album(album.id)
                album.link(['Wo1JI_oZNyrfxV_t'])
                album.unlink(['Wo1JI_oZNyrfxV_t'])
                album.discard('test comment')

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

            collection_template_item = collection.item_template()
            self.assertEqual(collection_template_item.collectionId, collection.id)

            collection.dumps()
            if not self.api.service_mode_private:
                collection.release()

            repr(collection)

            collection2 = self.api.create('collection', title='abc', profile='dhV6XK39_UPrItK5')
            assert collection2
            collection2.delete()

            collection3 = self.api.create(
                'collection',
                title='cde',
                profile=self.api.profile('dhV6XK39_UPrItK5'))
            assert collection3

            collection.description='test description'
            collection= collection.save()
            assert collection

            collections = self.api.collections(size=500, q='Test', offset=0)
            self.assertEqual(self.api.total_number_of_results,1)
            self.assertEqual(self.api.number_of_results,1)
            self.assertEqual(self.api.offset,0)
            self.assertEqual(self.api.size,1)

            self.assertIn('FKMxUpYdV9N2J4XG', collections)
            with self.assertRaises(ValueError):
                self.api.collections(size=500, qquery='Test', offset=0)

    def test_item(self):
        with HTTMock(imeji):
            self.api.create('item', _file=__file__, filename='name.png')
            items = self.api.items()
            self.assertIn('Wo1JI_oZNyrfxV_t', items)
            item = self.api.item(list(items.keys())[0])
            self.assertEqual(item.filename, 'virr-image.tif')
            self.assertRaises(ValueError, self.api.item)
            self.assertRaises(AttributeError, getattr, item, 'abc')
            self.assertRaises(AttributeError, setattr, item, 'id', 'abc')
            item2 = self.api.create('item', collectionId='abc', file=__file__)
            assert item2
            item2.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.json')
            self.api.update(item2, filename='name.png')
            item2.delete()
            self.api.delete(item)
            collection = self.api.create(
                'collection',
                title='cde',
                profile=self.api.profile('dhV6XK39_UPrItK5'))
            item3= collection.add_item( _file=__file__)
            self.assertEqual(item3.filename, 'virr-image.tif')
            item3.filename='name.png'
            item3.save()
            self.assertEqual(item3.filename, 'name.png')
            item3=self.api.update(item3, filename='virr-image.tif')
            assert item3
            with self.assertRaises(AttributeError):
                item3=self.api.update(item3, metadata='some metadata')

    def test_profile(self):
        with HTTMock(imeji):
            profile = self.api.profile('dhV6XK39_UPrItK5')
            self.assertEqual(profile.title, 'METADATA PROFILE VIA REST')
            profile.title = "NEW PROFILE TITLE"
            profile_template_item = profile.item_template()
            self.assertEqual(profile_template_item.collectionId, 'provide-your-collection-id-here')
            profile1 = profile.copy()
            profile.delete()
            assert profile1

    def test_cli(self):
        from pyimeji.cli import main
        from pyimeji.resource import Collection

        with HTTMock(imeji):
            res = main(
                ('--service=%s retrieve collection FKMxUpYdV9N2J4XG' % SERVICE_URL)
                    .split())
            self.assertIsInstance(res, Collection)


class ServiceTest(TestCase):
    from pyimeji.api import ImejiError

    @raises(ImejiError)
    def test_service_setup(self):
        from pyimeji.api import Imeji
        Imeji(service_url=SERVICE_URL + "FAKE")

    @raises(ImejiError)
    def test_service_unavailable_in_meantime_setup(self):
        from pyimeji.api import Imeji
        with HTTMock(imeji):
            api = Imeji(service_url=SERVICE_URL)
            api.service_url = "http://non_existing_service"
            api._req(SERVICE_URL, json_res=True, assert_status=200)
