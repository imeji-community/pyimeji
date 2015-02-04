import os
import json

from six import string_types
from dateutil.parser import parse

from pyimeji.util import jsonload


class ReadOnlyAttributeError(AttributeError):
    pass


class Resource(object):
    __readonly__ = ['id', 'createdBy', 'modifiedBy', 'createdDate', 'modifiedDate']
    __subresources__ = []

    def __init__(self, d, api):
        self._api = api
        self._json = d
        for k, v in d.items():
            try:
                self.__setattr__(k, v)
            except ReadOnlyAttributeError:
                pass

    def _path(self, *comps):
        _comps = ['/%ss' % self.__class__.__name__.lower()]
        if self._json.get('id'):
            _comps.append(self.id)
        return '/'.join(_comps + list(comps))

    def __getattr__(self, attr):
        """Attribute lookup.

        Attributes provide easy access to the following things:

        - subresources,
        - top-level keys in the resource's JSON representation.
        """
        if attr in self.__subresources__:
            # we fetch subresources using an API call when the corresponding attribute
            # is accessed - every time.
            json = True if not isinstance(self.__subresources__, dict) \
                else self.__subresources__[attr]
            return self._api._req(self._path() + '/' + attr, json=json)
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
        return json.dumps(self._json, **kw)

    def __repr__(self):
        return self.dumps(sort_keys=True, indent=4, separators=(',', ': '))

    def save(self):
        kw = dict(
            method='put' if self._json.get('id') else 'post',
            data=self.dumps(),
            headers={'content-type': 'application/json'})
        if kw['method'] == 'post':
            kw['assert_status'] = 201
        return self.__class__(self._api._req(self._path(), **kw), self._api)

    def delete(self):
        return self._api._req(
            self._path(), method='delete', assert_status=204, json=False)


class Collection(Resource):
    def add_item(self, **kw):
        return self._api.create('item', collectionId=self.id, **kw)

    def release(self):
        return self._api._req(
            self._path('release'), method='put', assert_status=200, json=False)

    def __setattr__(self, attr, value):
        if attr == 'profile':
            if isinstance(value, string_types):
                value = dict(profileId=value, method="copy")
            elif isinstance(value, Profile):
                value = dict(profileId=value.id, method="copy")
        Resource.__setattr__(self, attr, value)


class Profile(Resource):
    pass


class Item(Resource):
    __subresources__ = {'content': False}

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
            value = jsonload(value)
        Resource.__setattr__(self, attr, value)

    @_file.setter
    def _file(self, value):
        assert os.path.exists(value)
        self.__file = value

    def save(self):
        # FIXME: verify md5 sum upon creation of item from local file!
        kw = dict(
            method='put' if self._json.get('id') else 'post',
            assert_status=200 if self._json.get('id') else 201,
            files=dict(json=self.dumps(), file=''))
        if self._file:
            kw['files']['file'] = open(self._file, 'rb')
        return self.__class__(
            self._api._req(self._path(), **kw),
            self._api)
