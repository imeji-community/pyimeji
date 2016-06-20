import os
import json
from collections import OrderedDict

from six import string_types
from dateutil.parser import parse


class ReadOnlyAttributeError(AttributeError):
    pass


class Resource(object):
    """
    Super class implementing common methods for other resource objects

    """
    __readonly__ = ['id', 'createdBy', 'modifiedBy', 'createdDate', 'modifiedDate']

    def __init__(self, d, api, parent=None):
        self._api = api
        self._json = d
        self._parent = parent
        for k, v in d.items():
            try:
                self.__setattr__(k, v)
            except ReadOnlyAttributeError:
                pass

    def _path(self, *comps, **kw):
        _comps = []
        if self._parent:
            _comps = ['/%ss' % self._parent.__class__.__name__.lower(), self._parent.id]
        _comps.append('/%ss' % self.__class__.__name__.lower())
        if self._json.get('id') and not kw.get('batch'):
            _comps.append(self.id)
        return '/'.join(_comps + list(comps))

    def __getattr__(self, attr):
        """Attribute lookup.

        Attributes provide easy access to the following things:

        - top-level keys in the resource's JSON representation.

        """
        try:
            res = self._json[attr]
        except KeyError:
            raise AttributeError(attr)

        if attr.endswith('Date'):
            res = parse(res)

        #
        # TODO: once this is available, resolve users to proper objects upon access!
        #
        return res

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            return object.__setattr__(self, attr, value)
        if attr in self.__readonly__:
            raise ReadOnlyAttributeError('%s is readonly' % attr)
        self._json[attr] = value

    def dumps(self, **kw):
        """
        Provides a JSON serialization of the resources.

        """
        return json.dumps(self._json, **kw)

    def __repr__(self):
        return self.dumps(sort_keys=True, indent=4, separators=(',', ': '))

    def save(self):
        """
            Saves the object upon which it is called (creates new or updates an existing one) and invokes the REST API of the imeji instance.
            If the "id" of the object is provided, it attempt to update an existing object, otherwise, new object will be created.
        """
        kw = dict(
            method='put' if self._json.get('id') else 'post',
            data=self.dumps(),
            headers={'content-type': 'application/json'})
        if kw['method'] == 'post':
            kw['assert_status'] = 201
        return self.__class__(self._api._req(self._path(), **kw), self._api)

    def delete(self):
        """
            Deletes the object with provided Id.
        """
        return self._api._req(
            self._path(), method='delete', assert_status=204, json_res=False)


class _WithAuthor(Resource):
    """
        Supports creation of Collection or Album resources with or without contributors.
    """

    def __init__(self, d, api):
        if 'contributors' not in d:
            d['contributors'] = [
                {
                    'familyName': 'none',
                    'organizations': [{'name': 'none'}]}]
        Resource.__init__(self, d, api)


class _DiscardReleaseMixin(object):
    """
        Supports releasing or discarding of imeji objects of type Collection, Item or Album.
        If Imeji Instance runs in private modus, then no release or discard is allowed.
        The method will return "code 405 Method Not Allowed" as response.
    """

    def discard(self, comment):
        """
            Discard the object - object will no longer be public, and its fulltext is no longer accessible.
            This method is not allowed in "private" mode.
            param: reason to discard the object
        """
        return self._api._req(
            self._path('discard'),
            data=dict(id=self.id, discardComment=comment),
            method='put',
            assert_status=200 if not self._api.service_mode_private else 405, json_res=False)

    def release(self):
        """
            Release the object - object will be publicly available and its fulltext will be publicly accessible.
            This method is not allowed in "private" mode.
        """
        return self._api._req(
            self._path('release'),
            method='put',
            assert_status=200 if not self._api.service_mode_private else 405, json_res=False)


class Album(_WithAuthor, _DiscardReleaseMixin):
    """
        An aggregation of more imeji items (only item references), useful for creation of "special" views of imeji
        data independent of the item collection. An item may be referenced by many albums.
    """

    def members(self, **kw):
        """
            Lists all items which are members of the current album. Accepts q (fulltext query), size and offset parameters.
            The default value of size is "20".
        """
        return OrderedDict(
            [(d['id'], d) for d in self._api._req(self._path('items'), params=kw)])

    def member(self, id):
        """
            Gets an item with provided id (which is a member of the current album)
        """
        for id_, d in self.members().items():
            if id_ == id:
                return Resource(d, self._api, parent=self)

    def _act_on_members(self, op, *ids, **kw):
        return self._api._req(
            self._path('members', op), method='put', data=json.dumps(*ids), **kw)

    def link(self, *ids):
        """
            Links members in the album
            :param: List of item identifiers which need to be added to the current album e.g. [id-1, id-2, .., id-n]
        """
        return self._act_on_members('link', *ids)

    def unlink(self, *ids):
        """
            Unlinks members from the album
            :param: List of item identifiers which need to be unlinked from the current album
                e.g. [id-1, id-2, .., id-n]
        """
        return self._act_on_members('unlink', *ids, **{'assert_status': 204})


class Collection(_WithAuthor, _DiscardReleaseMixin):
    """
        Collection is basic container (context) for administration of items in imeji. Each item in imeji may be
        administered in at most one collection.
    """

    def items(self, **kw):
        """
          Lists all items within current collection. Accepts q (fulltext query), size and offset parameters.
          The default value of size is "20".
        """
        return OrderedDict(
            [(d['id'], d) for d in self._api._req(self._path('items'), params=kw)])

            # ['id']: Item(d, self._api) for d in
            # self._api._req(self._path('items'), params=kw)}

    def add_item(self, **kw):
        """
            Creates a new item within the current collection. It accepts a url or a file
            and a JSON-formatted metadata in the body.

            Check the `REST API documentation for item creation
            <https://github.com/imeji-community/imeji/wiki/Items:-Create-new-item">`_
            for more information about the possible parameters.

            :rtype: Item

        """
        return self._api.create('item', collectionId=self.id, **kw)

    def __setattr__(self, attr, value):
        if attr == 'profile':
            if isinstance(value, string_types):
                value = dict(profileId=value, method="copy")
            elif isinstance(value, Profile):
                value = dict(profileId=value.id, method="copy")
        Resource.__setattr__(self, attr, value)

    def save(self):
        """
            Creates a new item or updates an existing collection, depending if "id" parameter is provided
            in the JSON body of the request or not.

            :rtype: Collection
        """
        if self._json.get('id'):
            kw = dict(method='put' if self._json.get('id') else 'post', data=self.dumps(),
                      headers={'Content-Type': 'application/json'})
            return self.__class__(self._api._req(self._path(), **kw), self._api)
        return Resource.save(self)

    def item_template(self):
        """
            Retrieves an item template in a JSON format in accordance with the current metadata
             profile of the current collection.

            :rtype: Item

        """
        json_item = self._api._req(self._path('items/template'))
        return Item(json_item, self._api._req(self._path('items')))


class Profile(Resource, _DiscardReleaseMixin):
    """
        A Metadata profile structurally defines a set of metadata which may be used to describe an item in imeji. For example,
        a metadata profile may contain "title", "description", "author", "shelfmark" etc as metadata.
        In imeji, metadata profiles can be freely defined by the users for various types of item resources.
        A collection may only have one single metadata profile. All items within the collection can be described
        with the collection metadata profile only.
        However, each collection in imeji may have own specific metadata profile to be applied to the collection items.
    """

    def item_template(self):
        """
        Retrieves an item template in a JSON format in accordance with the current metadata profile.

        :rtype: Item
        """
        json_item = self._api._req(self._path('template'))
        return Item(json_item, self._api._req(self._path('template')))

    def copy(self):
        """
         Copies the current metadata profile and returns the copied metadata profile.

        :rtype: Profile
        """
        return Profile(
            self._api._req(self._path(batch=True),
                           method='post',
                           json_res=True,
                           assert_status=201,
                           data=self.dumps()),
            self._api._req(self._path()))


class Item(Resource):
    """
        Items are basic content resources in imeji. An item can be created within one collection,
        and aggregated by many albums. An item in imeji is described with metadata, which are defined through
        the metadata profile of the collection. An item in imeji may contain any binary content
        (e.g. pdf, image, video, text, csv etc.) or reference external content
        via an URL. Contained binary content may be uploaded from local storage or
        "fetched" by imeji from publicly accessible URL.
    """

    def __init__(self, d, api):
        self.__file = None
        _file = d.pop('_file', None)
        if _file:
            setattr(self, '_file', _file)
        Resource.__init__(self, d, api)

    @property
    def _file(self):
        return self.__file

    def __setattr__(self, attr, value):
        if attr == 'metadata' and isinstance(value, string_types):
            # if a string is passed as metadata, it is interpreted as filename.
            # NB 19.05.2016: this makes no sense and it changes the API use in unforeseen manner
            # value = jsonload(value)
            raise AttributeError(attr)
        Resource.__setattr__(self, attr, value)

    @_file.setter
    def _file(self, value):
        assert os.path.exists(value)
        self.__file = value

    def save(self):
        """
            Saves the Item object and creates a new item, or updates an existing item.

            :rtype: Item
        """
        # FIXME: verify md5 sum upon creation of item from local file!
        kw = dict(
            method='put' if self._json.get('id') else 'post',
            assert_status=200 if self._json.get('id') else 201,
            files=dict(json=self.dumps()))

        if self._file:
            kw['files']['file'] = open(self._file, 'rb')

        return self.__class__(self._api._req(self._path(), **kw), self._api)
