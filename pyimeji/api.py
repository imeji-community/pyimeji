"""A client for the REST API of imeji instances."""
import logging
from collections import OrderedDict

import requests
from six import string_types

from pyimeji import resource
from pyimeji.config import Config

log = logging.getLogger(__name__)


class ImejiError(Exception):
    def __init__(self, message, error):
        super(ImejiError, self).__init__(message)
        self.error = error.get('error') if isinstance(error, dict) else error


class _GET(object):
    """Handles GET requests.

    This includes requests

    - to retrieve single objects,
    - to fetch lists of object references (which are returned as `OrderedDict` mapping
      object `id` to additional metadata present in the response).
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

    def __call__(self, id='', **kw):
        """Calling the handler initiates an HTTP request to the imeji server.

        :param id: If a single object is to be retrieved it must be specified by id.
        :return: An OrderedDict mapping id to additional metadata for lists, a \
        :py:class:`pyimeji.resource.Resource` instance for single objects.
        """
        if not self._list and not id:
            raise ValueError('no id given')
        if id:
            id = '/' + id

        res = self.api._req('/%s%s' % (self.path, id), params=kw)

        if not self._list:
            return self.rsc(res, self.api)

        return OrderedDict([(d["id"], d) for d in res])


class Imeji(object):
    """The client.

        .. seealso:: The imeji software REST API is documented at https://github.com/imeji-community/imeji/wiki/A_Home-imeji-API-V1

        Below some more usage examples:

            >>> # Initiate the imeji API via pyimeji
            >>> api = Imeji(service_url='http://demo.imeji.org/imeji/')
            >>> # Get the id of the first collection from the list of first 100
            >>> # collections which contain "test" in their metadata
            >>> collection_id = list(api.collections(size=100, q="test").keys())[0]
            >>> # retrieve the collection with id='collection_id'
            >>> collection = api.collection('collection_id')
            >>> # create a new collection with a given title
            >>> collection = api.create('collection', title='the new collection')
            >>> # change the title and update it
            >>> collection.title="the new title"
            >>> collection.save()
            >>> # add new item in the collection, and fetch the content from the provided URL
            >>> item = collection.add_item(fetchUrl='http://example.org')
            >>> # retrieve and delete an item
            >>> item = api.item('item_id')
            >>> item.delete()
            >>>
            >>> # to quickly get the total number of items in a collection or matching a query
            >>> # set the size parameter to a value of 0
            >>> items= api.collection('collection_id').items(size=0, q="test")
            >>> print (api.total_number_of_results)
            >>>

        More usage examples you may find in the test sources at **./tests/** e.g. ** live_test_usecases.py**, **test_api.py**
    """

    def __init__(self, cfg=None, service_url=None, service_mode=None):
        """

        :param cfg: Configuration for the service
        :param service_url: The service URL
        :param service_mode: set to "private" if imeji instance runs in "private" mode
           (any other value considered as standard imeji instance mode )

        If the imeji instance is not available or does not run, the instantiation will throw an error message.
        """
        self.cfg = cfg or Config()
        self.service_url = service_url or self.cfg.get('service', 'url')
        self.service_mode_private = False or (self.cfg.get('service', 'mode', 'public') == 'private' or service_mode == 'private')
        self.service_unavailable_message = \
            "WARNING : The REST Interface of Imeji at {rest_service} is not available or there is another problem, " \
            "check if the service is running under {imeji_service}" \
                .format(imeji_service=self.service_url, rest_service=self.service_url + '/rest')

        # check if Imeji instance is running and notify the user
        try:
            requests.head(self.service_url)
        except Exception as e:
            raise ImejiError(self.service_unavailable_message, e)

        user = self.cfg.get('service', 'user', default=None)
        password = self.cfg.get('service', 'password', default=None)
        self.session = requests.Session()
        if user and password:
            self.session.auth = (user, password)
        # initialize the request query
        self.total_number_of_results = self.number_of_results = self.offset = self.size = None

    def _req(self, path, method='get', json_res=True, assert_status=200, **kw):
        """Make a request to the API of an imeji instance.

        :param path: HTTP path.
        :param method: HTTP method.
        :param json: Flag signalling whether the response should be treated as JSON.
        :param assert_status: Expected HTTP response status of a successful request.
        :param kw: Additional keyword parameters will be handed through to the \
        appropriate function of the requests library.
        :return: The return value of the function of the requests library or a decoded \
        JSON object/array.
        """
        # Method GET parameter validation
        # if parameters are there
        if method == "get" and kw.get("params") and str(path).endswith("s"):
            req_params = kw.get("params")
            if req_params:
                can_params = {"size", "offset", "q"}
                if not (can_params >= set(req_params.keys())):
                    raise ValueError("Wrong set of parameters in the request " + str(set(req_params) - set(can_params)))
        # check if the instance has gone away in meantime
        try:
            method = getattr(self.session, method.lower())
            res = method(self.service_url + '/rest' + path, **kw)
        except Exception as e:
            raise ImejiError(self.service_unavailable_message, e)

        if assert_status:
            if res.status_code != assert_status:  # pragma: no cover
                err_message = 'Unexpected HTTP status code: got HTTP %s, expected HTTP %s' % (
                    res.status_code, assert_status)
                log.error(err_message)
                if hasattr(res, 'text'):
                    log.error(res.text[:1000])
                    try:
                        res_json = res.json()
                        if "error" in res_json \
                                and "exceptionReport" in res_json["error"] \
                                and "title" in res_json["error"]:
                            err_message += "\nDetails from response: " + res_json["error"]["title"] + ". " + \
                                           res_json["error"]["exceptionReport"]
                    except:
                        pass
                    log.error(res)
                raise ImejiError(err_message, res)

        if json_res:
            try:
                res = res.json()
                if "results" in res:
                    self.total_number_of_results = res["totalNumberOfResults"]
                    self.number_of_results = res["numberOfResults"]
                    self.offset = res["offset"]
                    self.size = res["size"]
                    res = res["results"]
            except ValueError:  # pragma: no cover
                log.error(res.text[:1000])
                pass
        return res

    def __getattr__(self, name):
        """
        Names of resource classes are accepted and resolved as dynamic attribute names.

        This allows convenient retrieval of resources as api.<resource-class>(id=<id>),
        or api.<resource-class>s(q='x').

        """
        return _GET(self, name)

    def create(self, rsc, **kw):
        if isinstance(rsc, string_types):
            cls = getattr(resource, rsc.capitalize())
            rsc = cls(kw, self)
        return rsc.save()

    def delete(self, rsc):
        return rsc.delete()

    def update(self, rsc, **kw):
        for k, v in kw.items():
            setattr(rsc, k, v)
        return rsc.save()
