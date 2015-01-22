import os
import json

from dateutil.parser import parse


class Resource(object):
    __readonly__ = ['id', 'createdBy', 'modifiedBy', 'createdDate', 'modifiedDate']
    __subresources__ = []

    def __init__(self, d, api):
        self._api = api
        self._json = d

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
            raise AttributeError('%s is readonly' % attr)
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
    __subresources__ = ['mdprofiles']

    def add_item(self, **kw):
        return self._api.create('item', collectionId=self.id, **kw)

    def release(self):
        return self._api._req(
            self._path('release'), method='put', assert_status=204, json=False)


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

    @_file.setter
    def _file(self, value):
        assert os.path.exists(value)
        self.__file = value

    def save(self):
        # FIXME: verify md5 sum upon creation of item from local file!
        return self.__class__(
            self._api._req(
                self._path(),
                method='put' if self._json.get('id') else 'post',
                assert_status=200 if self._json.get('id') else 201,
                files=dict(
                    file=open(self._file, 'rb') if self._file else '',
                    json=self.dumps())),
            self._api)
