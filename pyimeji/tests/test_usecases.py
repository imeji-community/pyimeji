__author__ = 'schudan'
from pyimeji.api import Imeji
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import unittest

tag = "automated test pyimeji"
testpath=os.path.dirname(os.path.abspath(__file__));

class SetUp(unittest.TestCase):
    def setUp(self):
        self.api = Imeji()

    def tearDown(self):
        #delete all collections with title  tag"
        collections = self.api.collections(size=500)
        for c in collections:
            if collections[c]["title"] == tag:
                self.api.delete (self.api.collection (c))

class TestUseCases(SetUp):
    def test_create_collection(self):
        collection = self.api.create('collection', title= tag)
        self.assertEqual(collection._json["title"], tag)

    def test_create_collection_with_metadata_add_item(self):
        default_profile = self.api.profile ("default")
        collection = self.api.create('collection', title=tag, profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.add_item (_file=testpath+"/resources/test.txt", metadata={"Title":"Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")

    def test_add_item_to_collection_by_file(self):
        collection = self.api.create ('collection', title=tag)
        item = collection.add_item (_file=testpath+"/resources/test.txt")
        self.assertEqual(item._json["filename"], "test.txt")

    def test_add_item_to_collection_by_fetchUrl(self):
        default_profile = self.api.profile("default")
        collection = self.api.create ('collection', title=tag, profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.add_item (fetchUrl="https://de.wikipedia.org/wiki/Max_Planck_Digital_Library#/media/File:MPI-Muc-Amalienstra%C3%9Fe.JPG",  metadata={"Title":"Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")
        #self.assertEqual(item._json["filename"], "File:MPI-Muc-Amalienstra%C3%9Fe.JPG")

    def test_add_item_to_collection_by_referenceUrl(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                       profile={'id': default_profile._json["id"], 'method': 'reference'})
        fileUrl= "https://de.wikipedia.org/wiki/Max_Planck_Digital_Library#/media/File:MPI-Muc-Amalienstra%C3%9Fe.JPG"
        item = collection.add_item(
            referenceUrl=fileUrl,
            metadata={"Title": "Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")
        self.assertEqual(item._json["fileUrl"], fileUrl)

    def test_get_items_template(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                       profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.item_template()
        self.assertEqual(item._json["collectionId"], collection._json["id"])
        self.assertEqual(item._json["metadata"]["Title"], "Textual value")
        self.assertEqual(item._json["metadata"]["Comment"], "Textual value")
        with self.assertRaises(KeyError):
            item._json["metadata"]["WhatevereElse"]
        self.assertEqual(item._json["filename"], "<change-the-file-name-here-or-provide-separate-field-for-fetch-or-reference-url-see-API-Documentation>")

    def test_get_items_template_emptyprofile(self):
        collection = self.api.create('collection', title=tag)
        item = collection.item_template()
        self.assertEqual(item._json["collectionId"], collection._json["id"])
        self.assertEqual(item._json["metadata"], {})
        self.assertEqual(item._json["filename"],
                         "<change-the-file-name-here-or-provide-separate-field-for-fetch-or-reference-url-see-API-Documentation>")

    def test_create_item_from_template(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                       profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.item_template()
        itemTitle= "Template Title Of The Item"
        item._json["metadata"]["Title"]=itemTitle
        item._json["metadata"]["Title"] = itemTitle
        item=collection.add_item(_file=testpath+"/resources/test.txt", filename=itemTitle+".txt", metadata=item._json["metadata"])
        assert(item)
        print(item)
        self.assertEqual(item._json["metadata"]["Title"], itemTitle)
        self.assertEqual(item._json["filename"], itemTitle+".txt")
        item.delete()

    def test_create_collection_and_Items_query_limit_offset(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'copy'})
        fileUrl="http://example.com"
        for i in range(1,6):
            newFileUrl=fileUrl+"."+str(i)
            item = collection.add_item(referenceUrl=newFileUrl, metadata={"Title": "Test"+str(i)})
        self.assertEqual(len(collection.items()), 5)
        queried_items=collection.items()
        self.assertEqual(len(queried_items),5)
        queried_items=collection.items(q="Test*")
        self.assertEqual(len(queried_items),5)
        queried_items=collection.items(q="Test*", size=2, offset=2)
        self.assertEqual(len(queried_items), 2)
        queried_items = collection.items(q="Test*", size=2, offset=4)
        self.assertEqual(len(queried_items), 1)
        self.assertEqual(self.api.number_of_results, 1)
        self.assertEqual(self.api.total_number_of_results, 5)
        self.assertEqual(self.api.size, 2)
        self.assertEqual(self.api.offset, 4)
        queried_items = collection.items(q="Test*", offset=0)
        self.assertEqual(len(queried_items), 5)
        self.assertEqual(self.api.number_of_results, 5)
        self.assertEqual(self.api.offset, 0)
        with self.assertRaises(ValueError):
            queried_items = collection.items(q="Test*", offset=0, somedata=3768)


    def test_items_query_limit_offset(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'copy'})
        fileUrl = "http://example.com"
        for i in range(1, 6):
            newFileUrl = fileUrl + "." + str(i)
            item = collection.add_item(referenceUrl=newFileUrl, metadata={"Title": "Test" + str(i)})
        self.assertEqual(len(collection.items()), 5)
        queried_items = collection.items()
        self.assertEqual(len(queried_items), 5)
        queried_items = collection.items(q="Test*")
        self.assertEqual(len(queried_items), 5)
        queried_items = collection.items(q="Test*", size=2, offset=2)
        self.assertEqual(len(queried_items), 2)
        queried_items = collection.items(q="Test*", size=2, offset=4)
        self.assertEqual(len(queried_items), 1)
        self.assertEqual(self.api.number_of_results, 1)
        self.assertEqual(self.api.total_number_of_results, 5)
        self.assertEqual(self.api.size, 2)
        self.assertEqual(self.api.offset, 4)
        queried_items = collection.items(q="Test*", offset=0)
        self.assertEqual(len(queried_items), 5)
        self.assertEqual(self.api.number_of_results, 5)
        self.assertEqual(self.api.offset, 0)
        with self.assertRaises(ValueError):
            queried_items = collection.items(q="Test*", offset=0, somedata=3768)



if __name__=='__main__':
    unittest.main()