import requests

from pyimeji import resource


RESOURCES = {
    'collection': [],
    'item': [],
    'profile': [],
}


class GET(object):
    """handles GET requests"""
    def __init__(self, api, name):
        self._list = name.endswith('s')
        self.rsc = name[:-1] if self._list else name
        assert self.rsc in RESOURCES
        self.api = api
        self.name = name
        self.path = name
        if not self._list:
            self.path += 's'

    def __call__(self, id=''):
        if not self._list and not id:
            raise ValueError('no id given')
        res = self.api._req('/%s/%s' % (self.path, id))
        if not self._list:
            res = getattr(resource, self.rsc.capitalize())(res)
        return res


class Imeji(object):
    def __init__(self, cfg=None, service_url=None):
        self.cfg = cfg
        self.service_url = service_url

    def _req(self, path, method='get'):
        method = getattr(requests, method)
        return method(self.service_url + '/rest' + path).json()

    def __getattr__(self, name):
        return GET(self, name)


#/items/<id>/content
#/collections
#
