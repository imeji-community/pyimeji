__author__ = 'schudan'
from pyimeji.api import Imeji
import requests
from requests.auth import HTTPBasicAuth
import json
import unittest

tag = "automated test pyimeji"

class SetUp(unittest.TestCase):
    def setUp(self):
        self.api = Imeji()

    def tearDown(self):

        #delete all collections with title  tag"
        collections = self.api.collections()
        for c in collections:
            if collections[c]["title"]==tag:
                self.api.delete(self.api.collection(c))

class TestUseCases(SetUp):
    def test_create_collection(self):
        collection = self.api.create('collection', title= tag)
        assert(collection._json["title"]== tag)

    def test_create_collection_with_metadata_add_item(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title = tag, profile={'id': default_profile._json["id"], 'method':'reference'})
        item = collection.add_item(_file = "../tests/resources/test.txt", metadata={"Title":"Test"})
        assert(item._json["metadata"]["Title"]=="Test")

    def test_add_item_to_collection_by_file(self):
        collection = self.api.create('collection', title= tag)
        item = collection.add_item(_file = "../tests/resources/test.txt")
        assert(item._json["filename"]=="test.txt")

    def test_add_item_to_collection_by_fetchUrl(self):
        collection = self.api.create('collection', title= tag)
        item = collection.add_item(fetchUrl = "https://de.wikipedia.org/wiki/Max_Planck_Digital_Library#/media/File:MPI-Muc-Amalienstra%C3%9Fe.JPG")
        assert(item._json["filename"]=="File:MPI-Muc-Amalienstra%C3%9Fe.JPG")

if __name__=='__main__':
    unittest.main()