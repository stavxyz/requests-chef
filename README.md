# requests-chef
[![latest](https://img.shields.io/pypi/v/requests-chef.svg)](https://pypi.python.org/pypi/requests-chef)  
[Chef auth](https://docs.chef.io/auth.html#authentication-headers) support for [Python-Requests](http://docs.python-requests.org/en/latest/)

```python
import requests_chef

auth = requests_chef.ChefAuth('chef-user', '~/chef-user.pem')
response = requests.get('https://api.chef.io/users/chef-user',
                        headers={'X-Chef-Version': '12.0.2'},
                        auth=auth)
response.json()

{'display_name': 'chef-user',
 'email': 'chef-user@example.com',
 'first_name': 'Chef',
 'last_name': 'User',
 'middle_name': '',
 'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIj...IDAQAB\n-----END PUBLIC KEY-----\n',
 'username': 'chef-user'}
```

### Install

This project currently requires [a fork](https://github.com/samstav/cryptography/tree/rsa-bypass-hash-on-signer) of [pyca/cryptography](https://github.com/pyca/cryptography) due to the following related issues: 

* [#1648: decouple hashing process from signature generation / verification](https://github.com/pyca/cryptography/issues/1648)  
* [#1579: Support asymmetric signing with pre-computed digest](https://github.com/pyca/cryptography/issues/1579)

##### Instructions

*First*, install this fork of cryptography directly from github.

```
$ pip install git+https://github.com/samstav/cryptography.git@rsa-bypass-hash-on-signer
```

If you don't do this first, you'd have to use the (deprecated, scheduled for removal) `--process-dependency-links` option through pip, since pip no longer respects [dependency links](https://pythonhosted.org/setuptools/setuptools.html#dependencies-that-aren-t-in-pypi) by default (as of pip 1.5).
```
$ pip install --process-dependency-links requests-chef 
```
<!--Convert this file to .rst: `pandoc --from=markdown_github --to=rst README.md --output=README.rst` -->
