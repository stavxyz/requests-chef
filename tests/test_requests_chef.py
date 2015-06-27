
import hashlib
import os
import random
import string
import unittest

import requests

from cryptography.hazmat import backends as crypto_backends
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

import requests_chef

TEST_PEM = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'test.pem')
assert os.path.isfile(TEST_PEM), "Test PEM file not found."


def ascii_digest(n=1000):
    # digest of some random text/data
    chars = ''.join([random.choice(string.ascii_letters)
                     for _ in xrange(n)])
    return hashlib.sha1(chars).digest()


class TestChefAuth(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # generate an rsa private key
        self.user = 'patsy'
        with open(TEST_PEM, 'r') as pkey:
            pkey = pkey.read()
        self.private_key = serialization.load_pem_private_key(
            pkey,
            password=None,
            backend=crypto_backends.default_backend())

    def setUp(self):
        req = {
            'method': 'GET',
            'url': 'http://chef-server.com',
            'data': ascii_digest(),
        }
        self.request = requests.Request(**req).prepare()

    def assert_xops_headers(self, request):
        self.assertIn('X-Ops-Sign', request.headers)
        self.assertIn('X-Ops-UserId', request.headers)
        self.assertIn('X-Ops-Timestamp', request.headers)
        self.assertIn('X-Ops-Content-Hash', request.headers)
        self.assertIn('X-Ops-Authorization-1', request.headers)

    def test_from_string(self):

        serialized_key = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        handler = requests_chef.ChefAuth(self.user, serialized_key)
        request = handler(self.request)
        self.assert_xops_headers(request)

    def test_from_requests_chef_rsakey_from_string(self):

        serialized_key = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        rsakey = requests_chef.RSAKey.load_pem(serialized_key)
        handler = requests_chef.ChefAuth(self.user, rsakey)
        request = handler(self.request)
        self.assert_xops_headers(request)

    def test_from_cryptography_rsaprivatekey(self):

        handler = requests_chef.ChefAuth(self.user, self.private_key)
        request = handler(self.request)
        self.assert_xops_headers(request)

    def test_from_requests_chef_rsakey_direct(self):

        rsakey = requests_chef.RSAKey(self.private_key)
        handler = requests_chef.ChefAuth(self.user, rsakey)
        request = handler(self.request)
        self.assert_xops_headers(request)



class TestChefAuthGeneratedKey(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # generate an rsa private key
        self.user = 'patsy'
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048,
            backend=crypto_backends.default_backend())

    def setUp(self):
        req = {
            'method': 'GET',
            'url': 'http://chef-server.com',
            'data': ascii_digest(),
        }
        self.request = requests.Request(**req).prepare()

    def assert_xops_headers(self, request):
        self.assertIn('X-Ops-Sign', request.headers)
        self.assertIn('X-Ops-UserId', request.headers)
        self.assertIn('X-Ops-Timestamp', request.headers)
        self.assertIn('X-Ops-Content-Hash', request.headers)
        self.assertIn('X-Ops-Authorization-1', request.headers)

    def test_from_string(self):

        serialized_key = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        handler = requests_chef.ChefAuth(self.user, serialized_key)
        request = handler(self.request)
        self.assert_xops_headers(request)

    def test_from_requests_chef_rsakey_from_string(self):

        serialized_key = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        rsakey = requests_chef.RSAKey.load_pem(serialized_key)
        handler = requests_chef.ChefAuth(self.user, rsakey)
        request = handler(self.request)
        self.assert_xops_headers(request)

    def test_from_cryptography_rsaprivatekey(self):

        handler = requests_chef.ChefAuth(self.user, self.private_key)
        request = handler(self.request)
        self.assert_xops_headers(request)

    def test_from_requests_chef_rsakey_direct(self):

        rsakey = requests_chef.RSAKey(self.private_key)
        handler = requests_chef.ChefAuth(self.user, rsakey)
        request = handler(self.request)
        self.assert_xops_headers(request)


if __name__ == '__main__':

    unittest.main()
