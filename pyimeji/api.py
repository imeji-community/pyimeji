import requests

from pyimeji import resource


class GET(object):
    """handles GET requests"""
    def __init__(self, api, name):
        self._list = name.endswith('s')
        self.rsc = getattr(resource, (name[:-1] if self._list else name).capitalize())
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
            res = self.rsc(res, self.api)
        return res


class Imeji(object):
    def __init__(self, cfg=None, service_url=None):
        self.cfg = cfg
        self.service_url = service_url

    def _req(self, path, method='get', json=True):
        method = getattr(requests, method)
        res = method(self.service_url + '/rest' + path)
        if json:
            res = res.json()
        return res

    def __getattr__(self, name):
        return GET(self, name)


#/items/<id>/content
#/collections
#
