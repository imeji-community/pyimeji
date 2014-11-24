import json

from dateutil.parser import parse


class Resource(object):
    """
           "createdBy": {
            "fullname": "Saquet",
            "id": "zhcQKsMR0A9SiC6x"
        },
        "modifiedBy": {
            "fullname": "admin",
            "id": "w7ZfmmC5LQR8KJIN"
        },
        "createdDate": "2014-10-09T13:01:254 +0200",
        "modifiedDate": "2014-11-19T14:50:218 +0100",
    """
    __readonly__ = ['id', 'createdBy', 'modifiedBy', 'createdDate', 'modifiedDate']

    def __init__(self, d):
        self._json = d

    def __getattr__(self, attr):
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

    def dumps(self):
        return json.dumps(self._json)
