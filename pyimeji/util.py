import os
import json
import io

from six import PY3

import pyimeji


def pkg_path(*comps):
    return os.path.join(os.path.dirname(pyimeji.__file__), *comps)


def jsonload(path, **kw):
    """python 2 + 3 compatible version of json.load.

    :return: The python object read from path.
    """
    _kw = {}
    if PY3:  # pragma: no cover
        _kw['encoding'] = 'utf8'
    with io.open(path, **_kw) as fp:
        return json.load(fp, **kw)


def jsondumps(obj):
    if PY3:
        return json.dumps(obj).encode('utf8')
    else:
        return json.dumps(obj)
