"""A client for the REST API of imeji instances."""
import requests
from six import string_types

from pyimeji import resource
from pyimeji.config import Config


class GET(object):
    """Handle GET requests.

    This includes requests

    - to retrieve single objects,
    - to fetch lists of object references.
    """
    def __init__(self, api, name):
        """Initialize a handler.

        :param api: An Imeji API instance.
        :param name: Name specifying the kind of object(s) to retrieve. We check whether\
        this name has a plural "s" to determine if a list is to be retrieved.
        """
        self._list = name.endswith('s')
        self.rsc = getattr(resource, (name[:-1] if self._list else name).capitalize())
        self.api = api
        self.name = name
        self.path = name
        if not self._list:
            self.path += 's'

    def __call__(self, id=''):
        """Calling the handler initiates an HTTP request to the imeji server.

        :param id: If a single object is to be retrieved it must be specified by id.
        :return: The pure JSON response for lists, a \
        :py:class:`pyimeji.resource.Resource` instance for single objects.
        """
        if not self._list and not id:
            raise ValueError('no id given')
        if id:
            id = '/' + id
        res = self.api._req('/%s%s' % (self.path, id))
        if not self._list:
            res = self.rsc(res, self.api)
        return res


class Imeji(object):
    """The client.

    >>> api = Imeji(service_url='http://demo.imeji.org/imeji/')
    >>> collection_id = list(api.collections().keys())[0]
    >>> collection = api.collection(collection_id)
    >>> collection = api.create('collection', title='the new collection')
    >>> item = collection.add_item(fetchUrl='http://example.org')
    >>> item.delete()
    """
    def __init__(self, cfg=None, service_url=None):
        self.cfg = cfg or Config()
        self.service_url = service_url or self.cfg.get('service', 'url')
        user = self.cfg.get('service', 'user', default=None)
        password = self.cfg.get('service', 'password', default=None)
        self.session = requests.Session()
        if user and password:
            self.session.auth = (user, password)

    def _req(self, path, method='get', json=True, assert_status=200, **kw):
        method = getattr(self.session, method.lower())
        res = method(self.service_url + '/rest' + path, **kw)
        if assert_status:
            assert res.status_code == assert_status
        if json:
            try:
                res = res.json()
            except ValueError:  # pragma: no cover
                pass
        return res

    def __getattr__(self, name):
        return GET(self, name)

    def create(self, rsc, **kw):
        if isinstance(rsc, string_types):
            cls = getattr(resource, rsc.capitalize())
            rsc = cls(kw, self)
        return rsc.save()

    def delete(self, rsc):
        return rsc.delete()
