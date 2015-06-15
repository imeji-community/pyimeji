import os
import json
from collections import OrderedDict

from six import string_types
from dateutil.parser import parse

from pyimeji.util import jsonload


class ReadOnlyAttributeError(AttributeError):
    pass


class Resource(object):
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


class WithAuthor(Resource):
    def __init__(self, d, api):
        if 'contributors' not in d:
            d['contributors'] = [
                {
                    'familyName': 'none',
                    'role': 'author',
                    'organizations': [{'name': 'none'}]}]
        Resource.__init__(self, d, api)


class DiscardReleaseMixin(object):
    def discard(self, comment):
        return self._api._req(
            self._path('discard'),
            data=dict(id=self.id, discardComment=comment),
            method='put',
            assert_status=200,
            json=False)

    def release(self):
        return self._api._req(
            self._path('release'), method='put', assert_status=200, json=False)


class Album(WithAuthor, DiscardReleaseMixin):
    def members(self):
        return OrderedDict(
            [(d['id'], d) for d in self._api._req(self._path('members'))])

    def member(self, id):
        for id_, d in self.members().items():
            if id_ == id:
                return Resource(d, self._api, parent=self)

    def _act_on_members(self, op, *ids, **kw):
        return self._api._req(
            self._path('members', op), method='put', data=json.dumps(ids), **kw)

    def link(self, *ids):
        return self._act_on_members('link', *ids)

    def unlink(self, *ids):
        return self._act_on_members('unlink', *ids, **{'assert_status': 204})


class Collection(WithAuthor, DiscardReleaseMixin):
    def items(self, q=None):
        return {
            d['id']: Item(d, self._api) for d in
            self._api._req(self._path('items'), params=dict(q=q) if q else {})}

    def add_item(self, syntax="",**kw):
        return self._api.create('item', collectionId=self.id, syntax=syntax,**kw)

    def __setattr__(self, attr, value):
        if attr == 'profile':
            if isinstance(value, string_types):
                value = dict(profileId=value, method="copy")
            elif isinstance(value, Profile):
                value = dict(profileId=value.id, method="copy")
        Resource.__setattr__(self, attr, value)

    def save(self, syntax=""):
        if self._json.get('id'):
            kw = dict(method='put', data=dict(json=self.dumps()))
            return self.__class__(self._api._req(self._path(), **kw), self._api)
        return Resource.save(self)


class Profile(Resource, DiscardReleaseMixin):
    pass


class Item(Resource):
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

    def save(self, syntax=""):
        # FIXME: verify md5 sum upon creation of item from local file!
        kw = dict(
            method='put' if self._json.get('id') else 'post',
            assert_status=200 if self._json.get('id') else 201,
            files=dict(json=self.dumps()),
            params={"syntax":syntax})

        if self._file:
            kw['files']['file'] = open(self._file, 'rb')
        return self.__class__(
            self._api._req(self._path(), **kw),
            self._api)

    def save2(self, json):
        # FIXME: verify md5 sum upon creation of item from local file!
        kw = dict(
            method = 'patch',
            assert_status=200 if self._json.get('id') else 201,
            json = json
        )
        return self.__class__(
            self._api._req(self._path(), **kw),
            self._api)