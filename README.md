# requests-chef
Chef authentication support for Python-Requests

```python
import requests_chef

auth = requests_chef.ChefAuth('chef-user', '~/chef-user.pem')
response = requests.get('https://api.chef.io/users/chef-user',
                        headers={'X-Chef-Version': '12.0.2'},
                        auth=auth)
print(response.json())

    {'display_name': 'chef-user',
     'email': 'chef-user@example.com',
     'first_name': 'Chef',
     'last_name': 'User',
     'middle_name': '',
     'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2jKHmagBMP9GxLQUxg05\nzDgvAyLo20CR/5EtyCUz6gqvknTWtWQ9PMr/ihWhJWNhFDQRiHIgU2CS7JjEOMtM\nO9HIuqdswF7rMgH29CPlThSarK04W6SkQJgUIHlJqbXkwWkrAgN3bOvxUZJ8gORL\nlF9fI737Xi4Udsa7ct4TeXytL0ozCmkrkPXAFHBgkfxcCs8Rg6KbIRcn9vXVS86c\nsDY6jfy5dEoxzu5F2DH3OsUr8Va7WD0J75lN1Ivl6Gw/pHSUbV1AWl6TwDcgNlUD\n7HSfWzMPgQZdbK2c7iBb54GYQeS8+IW+a1z5WlQHXxLZGG+XTy2788WbEjCgGedv\nOQIDAQAB\n-----END PUBLIC KEY-----\n'
     'username': 'chef-user'}
```



