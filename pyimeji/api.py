import requests

from pyimeji.collection import Collection


class Imeji(object):
    def __init__(self, cfg=None, service_url=None):
        self.cfg = cfg
        self.service_url = service_url

    def _req(self, path, method='get'):
        method = getattr(requests, method)
        return method(self.service_url + '/rest' + path).json()

    def collections(self):
        return self._req('/collections/')

    def collection(self, id_):
        return Collection(self._req('/collections/' + id_))


#/items/<id>/content
#/collections
#
