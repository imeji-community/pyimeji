Tutorial
--------

Installation
~~~~~~~~~~~~

From PyPI::

    pip install pyimeji

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

This file can be customized e.g. to provide connection info or to set the logging level:

.. code-block:: ini

    [logging]
    level = DEBUG

    [service]
    url = http://localhost/imeji
    user = ****
    password = ****
    service_mode=

.. note::

    The logging level will be passed on to the logger for the *requests* library, too. So
    setting it to ``DEBUG`` will add information about the HTTP connection to the log.

    The service_mode is additional setting, which needs to be synchronized with the service_mode of the running imeji instance.
    (at present, there is no possibility to get it from the rest interface).
    If the imeji instance runs in a private mode, then the service_mode in this configuration file shall be set to value of "private"
    If the imeji instance runs in a public mode, you do not need to set-up the service_mode

A data curation workflow
~~~~~~~~~~~~~~~~~~~~~~~~

In the following we use pyimeji to curate a data collection on an imeji instance.

1. Creating the collection:

.. code-block:: python

    >>> from pyimeji.api import Imeji
    >>> api = Imeji()
    >>> collection = api.create('collection', title='hello world!')

 1.1. Creating a collection with the default metadata profile referenced
 .. code-block:: python

    >>> from pyimeji.api import Imeji
    >>> api = Imeji()
    >>> collection = api.create('collection', title='hello world!', profile={'id': api.profile('default').id, 'method': 'reference'}

or: Getting a collection:

.. code-block:: python

    >>> from pyimeji.api import Imeji
    >>> api = Imeji()
    >>> collection = api.collection('id_of_collection')
    
2. Adding items:

The imeji API supports three ways of associating an item with a file, all three of which
you can use with *pyimeji*, too:

.. code-block:: python

    >>> item1 = collection.add_item(_file='/path/to/file/in/local/filesystem')
    >>> item2 = collection.add_item(fetchUrl='http://example.org/')
    >>> item3 = collection.add_item(referenceUrl='http://example.org')

3. Release a collection and all items:

Once a collection has items, it may be released:

.. code-block:: python

    >>> collection.release()
    >>> assert api.collection(collection.id).status == 'RELEASED'

.. note::

    Synchronisation of local objects and the server have to happen explicitely, i.e.
    when an object has been changed locally, these changes must be sent to the server
    calling the objects' ``save`` method and after changing the server state with methods
    like ``release``, the local objects have to be refreshed to reflect the updated state.

Albums:

Now these items can be aggregated in albums:

.. code-block:: python

    >>> album = api.create('album', title='hello world!')
    >>> album.link(*list(collection.items().keys()))
    

