
import datetime
import hashlib
import os
import random
import string
import tempfile
import unittest

import mock
import requests
import six

from cryptography.hazmat import backends as crypto_backends
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import requests_chef

TEST_PEM = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'test.pem')
assert os.path.isfile(TEST_PEM), "Test PEM file not found."


def ascii_digest(n=1024):
    # digest of some random text/data
    chars = ''.join([random.choice(string.ascii_letters)
                     for _ in xrange(n)])
    return hashlib.sha1(chars).hexdigest()


class TestChefAuth(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.user = 'patsy'
        with open(TEST_PEM, 'r') as pkey:
            pkey = pkey.read()
        self.private_key = serialization.load_pem_private_key(
            pkey,
            password=None,
            backend=crypto_backends.default_backend())
        self.data = '07af154a81a86ccec33c213a0c71487a19cc3b76'

    def setUp(self):
        req = {
            'method': 'GET',
            'url': 'http://chef-server.com',
            'data': self.data,
        }
        self.request = requests.Request(**req).prepare()

        # workaround for:
        #
        # TypeError: can't set attributes of built-in/extension
        #            type 'datetime.datetime'
        class MockDatetime(datetime.datetime):
            @classmethod
            def utcnow(cls):
                return original_datetime.utcnow()
        original_datetime, datetime.datetime = datetime.datetime, MockDatetime

        utcnow_patcher = mock.patch.object(
            requests_chef.mixlib_auth.datetime.datetime, 'utcnow')
        self.mock_utcnow = utcnow_patcher.start()
        self.mock_utcnow.return_value = datetime.datetime(
            2015, 6, 29, 15, 30, 22)
        self.addCleanup(utcnow_patcher.stop)

    def assert_xops_headers(self, request):
        self.assertEqual(
            request.headers['X-Ops-Authorization-1'],
            'nRO82dpi5XCH9AC2xM0iPzMBSpmLbazJaPa70X8h27KxRUYEEKUUBTcoM7zg'
        )
        self.assertEqual(
            request.headers['X-Ops-Authorization-2'],
            'P2FJQ3ppu3K9r8arv/fnenx2Lt6VK4rQivzrDFpsh3yuDLW3lJaXe2Co4yPA'
        )
        self.assertEqual(
            request.headers['X-Ops-Authorization-3'],
            'X67KCw6otyrUFwSblVEdAVRp5K3QlHrmVUzqGQyEMZNS2XCmdfVT7dswacso'
        )
        self.assertEqual(
            request.headers['X-Ops-Authorization-4'],
            'BuNG89DBAtSF3epxq/G9LqrrUOWywfm7L8iIk8hjr1fFTioWbsvhkB7jmopa'
        )
        self.assertEqual(
            request.headers['X-Ops-Authorization-5'],
            'LPEwUUFrkAf1o3RfxkawYbVdCJBj3Qja9qVlkTXE/ECVhi+uc+V1ThJZtkIH'
        )
        self.assertEqual(
            request.headers['X-Ops-Authorization-6'],
            'QGLcWHWLeiHMJMLZYKLW26NoDmwVPohANflsTEU9xQ=='
        )

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

    def test_rsakey_handles_text(self):
        rsakey = requests_chef.RSAKey(self.private_key)
        data = six.text_type(self.data)
        result = rsakey.sign(data)
        expected = ('MiCicRdNBa6hLya65Mtlp0mPr+1X01pW/mvXL6b'
                    'JLXi9QpJExAvX2OzqJ/oDRU/m+OMGoU7x3MOHi2'
                    'pJNtPcG4+3bs7mr9yzF9CvFas5+UzgvH2R3ooFy'
                    'GuEv1kTVPk6ul1ws6LewX+2DV1X6YXj0gJwO2UP'
                    'jt9wIho5LI+oKfCU1YcyfhKIpEruiMFqjWUKyqr'
                    '/teC80q6q1ku5sDhO7JQQbkEHgzxcF4Bxcm06Ku'
                    'rNJ+gYLHkPchQJKYPr6Ty024xwIJ5lg2Qm3a3cK'
                    'L70cEu7vM65Eru2JCbpmybjYwLhJmcyLHipyxlE'
                    'oD9r1ZzBjv5PAEoc3Ayba8d4B1A6bQ==')
        self.assertEqual(expected, result)

    def test_repr(self):
        handler = requests_chef.ChefAuth(self.user, self.private_key)
        expected = 'ChefAuth(patsy)'
        self.assertEqual(expected, repr(handler))


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

    def test_from_requests_chef_rsakey_from_path(self):
        serialized_key = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        sfx = 'requests-chef-tests.pem'
        with tempfile.NamedTemporaryFile(suffix=sfx, mode='w') as pem:
            pem.write(serialized_key)
            pem.flush()
            rsakey = requests_chef.RSAKey.load_pem(pem.name)
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


class TestChefAuthFails(unittest.TestCase):

    def test_missing_username_fails(self):
        with self.assertRaises(ValueError):
            requests_chef.ChefAuth(None, '.')

    def test_missing_pem_fails(self):
        with self.assertRaises(ValueError):
            requests_chef.ChefAuth('.', None)

    def test_missing_values_fail(self):
        with self.assertRaises(ValueError):
            requests_chef.ChefAuth(None, None)

    def test_bogus_keyvalue_fails(self):
        with self.assertRaises(ValueError) as error:
            requests_chef.ChefAuth('user', 'not-a-key-or-path-to-one')
        expected_message = 'Could not unserialize key data.'
        self.assertEqual(expected_message, six.text_type(error.exception))

    def test_requires_cryptography_rsaprivatekey(self):
        with self.assertRaises(TypeError):
            requests_chef.RSAKey('not-a-key-instance')


class TestDigester(unittest.TestCase):

    def setUp(self):
        # in python2 this is bytes, 3 this is unicode
        self.data = 'e394cd9ef34341ca9d592a8fb515a8d4f03c1219'
        self.expected_result = 'yZtNP9J1L//viv+CGWLGgUZof48='

    def test_handles_binary(self):
        data = six.binary_type(self.data)
        result = requests_chef.mixlib_auth.digester(data)
        self.assertEqual(self.expected_result, result)

    def test_handles_text(self):
        data = six.text_type(self.data, encoding='utf_8')
        result = requests_chef.mixlib_auth.digester(data)
        self.assertEqual(self.expected_result, result)


if __name__ == '__main__':

    unittest.main()
