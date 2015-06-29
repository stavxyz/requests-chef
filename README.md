# requests-chef
[![latest](https://img.shields.io/pypi/v/requests-chef.svg)](https://pypi.python.org/pypi/requests-chef)  
[Chef auth](https://docs.chef.io/auth.html#authentication-headers) support for Python-Requests

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

#### install

This project currently requires [a fork](https://github.com/samstav/cryptography/tree/rsa-bypass-hash-on-signer) of [pyca/cryptography](https://github.com/pyca/cryptography) due to the following related issues: 

https://github.com/pyca/cryptography/issues/1648
https://github.com/pyca/cryptography/issues/1579


