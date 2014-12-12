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


First steps
~~~~~~~~~~~

.. code-block:: python

    >>> from pyimeji.api import Imeji
    >>> api = Imeji()
    >>> collection = api.create('collection', title='hello world!')
