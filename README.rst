requests-chef
=============

| |latest|  |Circle CI|  |Coverage Status|  |Requirements Status|

`Chef auth <https://docs.chef.io/auth.html#authentication-headers>`__ support for `Python-Requests <http://docs.python-requests.org/en/latest/>`__
--------------------------------------------------------------------------------------------------------------------------------------------------
|

.. code:: python

    import requests
    import requests_chef

    auth = requests_chef.ChefAuth('chef-user', '~/chef-user.pem')
    response = requests.get('https://api.chef.io/users/chef-user',
                            headers={'X-Chef-Version': '12.0.2'},
                            auth=auth)
    response.json()
    ...
    {'display_name': 'chef-user',
     'email': 'chef-user@example.com',
     'first_name': 'Chef',
     'last_name': 'User',
     'middle_name': '',
     'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIj...IDAQAB\n-----END PUBLIC KEY-----\n',
     'username': 'chef-user'}

See `samstav/okchef <https://github.com/samstav/okchef>`__ first, since
thats generally more useful.
`okchef <https://github.com/samstav/okchef>`__ uses
`requests-chef <https://github.com/samstav/requests-chef>`__ to sign
and authenticate requests.

Install
-------

This project currently requires `a
fork <https://github.com/samstav/cryptography/tree/rsa-bypass-hash-on-signer>`__
of `pyca/cryptography <https://github.com/pyca/cryptography>`__ due to
the following related issues:

-  `#1648: decouple hashing process from signature generation /
   verification <https://github.com/pyca/cryptography/issues/1648>`__
-  `#1579: Support asymmetric signing with pre-computed
   digest <https://github.com/pyca/cryptography/issues/1579>`__

Instructions
~~~~~~~~~~~~

*First*, install this fork of cryptography directly from github.

::

    $ pip install git+https://github.com/samstav/cryptography.git@rsa-bypass-hash-on-signer

If you don't do this first, you'd have to use the (deprecated, scheduled
for removal) ``--process-dependency-links`` option through pip, since
pip no longer respects `dependency
links <https://pythonhosted.org/setuptools/setuptools.html#dependencies-that-aren-t-in-pypi>`__
by default (as of pip 1.5).

::

    $ pip install --process-dependency-links requests-chef 

.. |latest| image:: https://img.shields.io/pypi/v/requests-chef.svg
   :target: https://pypi.python.org/pypi/requests-chef
.. |Circle CI| image:: https://circleci.com/gh/samstav/requests-chef/tree/master.svg?style=shield
   :target: https://circleci.com/gh/samstav/requests-chef
.. |Coverage Status| image:: https://coveralls.io/repos/samstav/requests-chef/badge.svg
   :target: https://coveralls.io/r/samstav/requests-chef
.. |Requirements Status| image:: https://requires.io/github/samstav/requests-chef/requirements.svg?branch=master
   :target: https://requires.io/github/samstav/requests-chef/requirements/?branch=master
