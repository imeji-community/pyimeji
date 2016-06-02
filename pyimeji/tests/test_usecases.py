from pyimeji.api import Imeji, ImejiError
import os
import unittest

tag = "automated test pyimeji"
testpath = os.path.dirname(os.path.abspath(__file__))
defaultFilename = "<change-the-file-name-here-or-provide-separate-field-for-fetch-or-reference-url-see-API-Documentation>"


class SetUp(unittest.TestCase):
    def setUp(self):
        self.api = Imeji()
        # if not self.api


    def tearDown(self):
        # delete all collections with title  tag"
        collections = self.api.collections(size=500)
        for c in collections:
            if tag in collections[c]["title"]:
                self.api.delete(self.api.collection(c))


        albums = self.api.albums(size=500)
        for c in albums:
            if tag in albums[c]["title"]:
                self.api.delete(self.api.album(c))


class TestUseCases(SetUp):
    def test_create_collection(self):
        collection = self.api.create('collection', title=tag)
        self.assertEqual(collection._json["title"], tag)

    def test_create_collection_with_metadata_add_item(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.add_item(_file=testpath + "/resources/test.txt", metadata={"Title": "Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")

    def test_add_item_to_collection_by_file(self):
        collection = self.api.create('collection', title=tag)
        item = collection.add_item(_file=testpath + "/resources/test.txt")
        self.assertEqual(item._json["filename"], "test.txt")

    def test_add_item_to_collection_by_fetchUrl(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.add_item(
            fetchUrl="https://de.wikipedia.org/wiki/Max_Planck_Digital_Library#/media/File:MPI-Muc-Amalienstra%C3%9Fe.JPG",
            metadata={"Title": "Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")
        self.assertEqual(item._json["filename"], "File:MPI-Muc-Amalienstra%C3%9Fe.JPG")

    def test_add_item_to_collection_by_referenceUrl(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'reference'})
        file_url = "https://de.wikipedia.org/wiki/Max_Planck_Digital_Library#/media/File:MPI-Muc-Amalienstra%C3%9Fe.JPG"
        item = collection.add_item(
            referenceUrl=file_url,
            metadata={"Title": "Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")
        self.assertEqual(item._json["fileUrl"], file_url)

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
        self.assertEqual(item._json["filename"], defaultFilename)

    def test_get_items_template_emptyprofile(self):
        collection = self.api.create('collection', title=tag)
        item = collection.item_template()
        self.assertEqual(item._json["collectionId"], collection._json["id"])
        self.assertEqual(item._json["metadata"], {})
        self.assertEqual(item._json["filename"], defaultFilename)

    def test_create_item_from_template(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'reference'})
        item = collection.item_template()
        item_title = "Template Title Of The Item"
        item._json["metadata"]["Title"] = item_title
        item._json["metadata"]["Title"] = item_title
        item = collection.add_item(_file=testpath + "/resources/test.txt", filename=item_title + ".txt",
                                   metadata=item._json["metadata"])
        assert item
        self.assertEqual(item._json["metadata"]["Title"], item_title)
        self.assertEqual(item._json["filename"], item_title + ".txt")
        item.delete()

    def test_create_collection_and_Items_query_limit_offset(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'copy'})
        file_url = "http://example.com"
        for i in range(1, 6):
            new_file_url = file_url + "." + str(i)
            collection.add_item(referenceUrl=new_file_url, metadata={"Title": "Test" + str(i)})
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
            collection.items(q="Test*", offset=0, somedata=3768)

    def test_items_query_limit_offset(self):
        default_profile = self.api.profile("default")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': default_profile._json["id"], 'method': 'copy'})
        file_url = "http://example.com"
        for i in range(1, 6):
            new_file_url = file_url + "." + str(i)
            collection.add_item(referenceUrl=new_file_url, metadata={"Title": "Test" + str(i)})
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
            collection.items(q="Test*", offset=0, somedata=3768)

    def test_collections_query_limit_offset(self):
        default_profile = self.api.profile("default")
        for i in range(1, 6):
            self.api.create('collection', title=tag,
                            profile={'id': default_profile._json["id"],
                                     'method': 'copy'},
                            description="query collection description " + str(i))

        self.api.collections(q="\"query collection description\"")
        self.assertEqual(self.api.total_number_of_results, 5)
        self.assertEqual(self.api.number_of_results, 5)
        self.assertEqual(self.api.offset, 0)

        self.api.collections(q="\"query collection description\"", size=3)
        self.assertEqual(self.api.total_number_of_results, 5)
        self.assertEqual(self.api.number_of_results, 3)
        self.assertEqual(self.api.offset, 0)

        # check if api size are reset
        self.api.items(q="\"query collection description\"", size=3)
        self.assertEqual(self.api.total_number_of_results, 0)
        self.assertEqual(self.api.number_of_results, 0)
        self.assertEqual(self.api.offset, 0)

        collection_id_to_update = list(self.api.collections(q="\"query collection description\"", size=1).keys())[0]
        collection_to_update = self.api.collection(collection_id_to_update)
        self.assertEqual(collection_to_update.title, tag)

        before_update_collection_description = collection_to_update.description
        collection_to_update.description = "updated " + collection_to_update.description
        collection_to_update.save()
        self.assertNotEqual(before_update_collection_description, collection_to_update.description)

        before_update_collection_description = collection_to_update
        collection_to_update.description = "updated " + collection_to_update.description
        collection_to_update = collection_to_update.save()
        self.assertNotEqual(before_update_collection_description, collection_to_update)

        before_update_additional_infos = collection_to_update
        collection_to_update.additionalInfos = \
            [{"label": "Label1", "text": "This is the text of Label 1", "url": "http://example.org"}]
        collection_to_update = collection_to_update.save()
        self.assertNotEqual(collection_to_update, before_update_additional_infos)

    def test_create_album_with_metadata_add_item(self):
        default_profile = self.api.profile("default")
        collection = self.api.create(
            'collection',
            title=tag,
            profile={'id': default_profile._json["id"],
                     'method': 'copy'})
        item = collection.add_item(
            _file=testpath + "/resources/test.txt",
            metadata={"Title": "Test"})
        self.assertEqual(item._json["metadata"]["Title"], "Test")
        item2 = collection.add_item(
            _file=testpath + "/resources/album.json",
            metadata={"Title": "Test"})

        album = self.api.create('album', title=tag, description=tag + " album ")
        my_list = [item.id, item2.id]
        album.link(my_list)
        self.assertEqual(len(album.members()), 2)
        self.assertEquals(item2.id, album.member(item2.id).id)
        self.assertEquals(album.member(item2.id).collectionId, collection.id)
        self.assertEqual(album.member(item2.id)._json["metadata"]["Title"], "Test")
        self.assertEquals(album.member("myarbitraryid"), None)
        my_list1 = my_list[:1]
        album.unlink(my_list1)
        self.assertEqual(len(album.members()), 1)
        album.link(my_list)
        self.assertEqual(len(album.members()), 2)
        album.unlink(my_list)
        self.assertEqual(len(album.members()), 0)

    def test_delete_default_profiles(self):
        default_profiles = self.api.profiles(size=500)
        for prof in default_profiles:
            if default_profiles[prof]["default"] == True and default_profiles[prof]["status"] != "RELEASED":
                self.api.delete(self.api.profile(prof))

    def test_copy_default_profiles(self):
        default_profile = self.api.profile("default")
        default_profile.title=default_profile.title+" A COPY OF THE DEFAULT PROFILE "
        new_profile = None

        with self.assertRaises(ImejiError):
            new_profile = default_profile.copy()

        default_profile.default=False
        new_profile=default_profile.copy()
        self.assertNotEquals(default_profile.id, new_profile.id)
        self.assertEquals(new_profile.default, False)
        default_profile=self.api.profile("default")
        self.assertEquals(new_profile.title, default_profile.title+" A COPY OF THE DEFAULT PROFILE ")
        self.assertEquals(len(new_profile.statements), len(default_profile.statements))


    def test_delete_profiles(self):
        profile = self.api.create("profile", title="delete profile test")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': profile.id, 'method': 'reference'})
        with self.assertRaises(ImejiError):
            profile.delete()

        collection.delete()
        profile.delete

        with self.assertRaises(ImejiError):
            self.api.profile(profile.id)

        with self.assertRaises(ImejiError):
            self.api.collection(collection.id)


    def test_release_withdaw_delete_profiles(self):
        profile = self.api.create("profile", title="discard profile test pyimeji")
        collection = self.api.create('collection', title=tag,
                                     profile={'id': profile.id, 'method': 'reference'})
        profile.release()

        with self.assertRaises(ImejiError):
            profile.delete()

        collection.delete()

        with self.assertRaises(ImejiError):
            profile.delete()

        profile.discard("discard profile test pyimeji")

if __name__ == '__main__':
    unittest.main()

