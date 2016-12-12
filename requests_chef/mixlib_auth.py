# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Chef rsa mixlib-authentication for python-requests

RSA public key-pairs are used to authenticate
the chef-client with the Chef server every
time a chef-client needs access to data that
is stored on the Chef server.

https://docs.chef.io/auth.html
"""

import base64
import collections
import datetime
import hashlib
import os

import requests
import six

from cryptography.hazmat import backends as crypto_backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils


def digester(data):
    """Create SHA-1 hash, get digest, b64 encode, split every 60 char."""
    if not isinstance(data, six.binary_type):
        data = data.encode('utf_8')
    hashof = hashlib.sha1(data).digest()
    encoded_hash = base64.b64encode(hashof)
    if not isinstance(encoded_hash, six.string_types):
        encoded_hash = encoded_hash.decode('utf_8')
    chunked = splitter(encoded_hash, chunksize=60)
    lines = '\n'.join(chunked)
    return lines


def normpath(path):
    """Normalize a path.

    Expands ~'s, resolves relative paths, normalizes and returns
    an absolute path.
    """
    return os.path.abspath(os.path.normpath(os.path.expanduser(path)))


def splitter(iterable, chunksize=60):
    """Split an iterable that supports indexing into chunks of 'chunksize'."""
    return (iterable[0+i:chunksize+i]
            for i in range(0, len(iterable), chunksize))


class ChefAuth(requests.auth.AuthBase):  # pylint: disable=R0903

    """Sign requests with user's private key.

    See https://docs.chef.io/auth.html
        https://docs.chef.io/auth.html#header-format
    """

    datetime_fmt = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, user_id, private_key):
        """Initialize with any callable handlers."""
        if not all((user_id, private_key)):
            raise ValueError("Authenticating to Chef server requires "
                             "both user_id and private_key.")
        if isinstance(private_key, rsa.RSAPrivateKey):
            private_key = RSAKey(private_key)
        elif isinstance(private_key, RSAKey):
            # good to go
            pass
        else:
            private_key = RSAKey.load_pem(private_key)
        self.private_key = private_key
        if not isinstance(user_id, six.string_types):
            raise TypeError(
                "'user_id' must be a 'str' object, not {0!r}".format(user_id))
        self.user_id = user_id

    def __repr__(self):
        """Show the auth handler object."""
        return '%s(%s)' % (type(self).__name__, self.user_id)

    def __call__(self, request):
        """Sign the request."""
        hashed_body = digester(request.body or '')
        stripped_path = request.path_url.partition('?')[0]
        hashed_path = digester(stripped_path)
        timestamp = datetime.datetime.utcnow().strftime(self.datetime_fmt)

        canonical_request = self.canonical_request(
            request.method, hashed_path, hashed_body, timestamp)

        signed = self.private_key.sign(canonical_request, b64=True)
        signed_chunks = splitter(signed, chunksize=60)
        signed_headers = {
            'X-Ops-Authorization-%d' % (i+1): segment
            for i, segment in enumerate(signed_chunks)
        }

        auth_headers = {
            'X-Ops-Sign': 'algorithm=sha1;version=1.0',
            'X-Ops-UserId': self.user_id,
            'X-Ops-Timestamp': timestamp,
            'X-Ops-Content-Hash': hashed_body,
        }

        auth_headers.update(signed_headers)
        request.headers.update(auth_headers)

        return request

    def canonical_request(self, method, path, content, timestamp):
        """Return the canonical request string."""
        request = collections.OrderedDict([
            ('Method', method.upper()),
            ('Hashed Path', path),
            ('X-Ops-Content-Hash', content),
            ('X-Ops-Timestamp', timestamp),
            ('X-Ops-UserId', self.user_id),
        ])
        return '\n'.join(['%s:%s' % (key, value)
                          for key, value in request.items()])


class RSAKey(object):

    """Requires an instance of RSAPrivateKey to initialize.

    The base class for this type is found in the crytography library
    at cryptography.hazmat.primitives.asymmetric.rsa
    """

    def __init__(self, private_key):
        """Requires an RSAPrivateKey instance.

        Key class from cryptography.hazmat.primitives.asymmetric.rsa
        """
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise TypeError("private_key must be an instance of "
                            "cryptography-RSAPrivateKey.")
        self.private_key = private_key

    @classmethod
    def load_pem(cls, private_key, password=None):
        """Return a PrivateKey instance.

        :param private_key: Private key string (PEM format) or the path
                            to a local private key file.
        """
        # TODO(sam): try to break this in tests
        maybe_path = normpath(private_key)
        if os.path.isfile(maybe_path):
            with open(maybe_path, 'rb') as pkf:
                private_key = pkf.read()
        if not isinstance(private_key, six.binary_type):
            private_key = private_key.encode('utf-8')

        pkey = serialization.load_pem_private_key(
            private_key,
            password=password,
            backend=crypto_backends.default_backend())
        return cls(pkey)

    def sign(self, data, b64=True):
        """Sign data with the private key and return the signed data.

        The signed data will be Base64 encoded if b64 is True.
        """
        if not isinstance(data, six.binary_type):
            data = data.encode('utf_8')

        signature = self.private_key.sign(
            hashlib.sha1(data).digest(),
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA1())
        )
        if b64:
            signed = base64.b64encode(signature)

        return signed
