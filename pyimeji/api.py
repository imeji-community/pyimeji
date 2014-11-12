import requests


class Imeji(object):
    def __init__(self, cfg=None, service_url=None):
        self.cfg = cfg
        self.service_url = service_url

    def _req(self, path, method='get'):
        method = getattr(requests, method)
        return method(self.service_url + path).json()

    @property
    def collections(self):
        return self._req('/collections/')


#/items/<id>/content
#/collections
#
