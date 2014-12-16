Tutorial
--------

Installation
~~~~~~~~~~~~

From GitHub::

    git clone https://github.com/imeji-community/pyimeji.git
    cd pyimeji
    python setup.py develop

Or better yet, fork the repos and install from your fork. Thus you'll be able to not only
report bugs, but maybe even fix them and submit pull requests.


Configuration
~~~~~~~~~~~~~

Upon first instantiation of an :py:class:pyimeji.api.Imeji`` object, a configuration will
be placed into the users `configuration directory <https://pypi.python.org/pypi/appdirs>`_.

This file can be customized e.g. to provide connection info:

.. code-block:: ini

    [logging]
    level = DEBUG

    [service]
    url = http://localhost/imeji
    user = ****
    password = ****


A data curation workflow
~~~~~~~~~~~~~~~~~~~~~~~~

In the following we use pyimeji to curate a data collection on an imeji instance.

1. Creating the collection:

.. code-block:: python

    >>> from pyimeji.api import Imeji
    >>> api = Imeji()
    >>> collection = api.create('collection', title='hello world!')

2. Adding items:

.. code-block:: python

    >>> item1 = collection.add_item(_file='/path/to/file/in/local/filesystem')
    >>> item2 = collection.add_item(fetchUrl='http://example.org/')
    >>> item3 = collection.add_item(referenceUrl='http://example.org')
