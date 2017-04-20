import jwt
from cryptography.x509 import load_pem_x509_certificate
from werkzeug.http import parse_cache_control_header
from time import monotonic
import requests
from cryptography.hazmat.backends import default_backend
from threading import Lock


class JwtParser:
    KEYCHAIN_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'  # noqa

    def __init__(self):
        self.keys = {}
        self.max_age = 0
        self.cached_at = 0
        self.lock = Lock()

    def parse_key(self, token_data, app):
        header = jwt.get_unverified_header(token_data)
        with self.lock:
            self.refresh_keys()
            key = self.keys[header['kid']]
        token = jwt.decode(
            token_data,
            key=key,
            audience=app.config['FIREBASE_PROJECT_ID'],
            algorithms=['RS256'])
        return token

    def refresh_keys(self):
        now = monotonic()
        age = now - self.cached_at
        if age >= self.max_age:
            response = requests.get(self.KEYCHAIN_URL)
            if response.status_code != 200:
                raise Exception
            hazmat = default_backend()
            for kid, text in response.json().items():
                certificate = load_pem_x509_certificate(
                    bytes(text, 'utf-8'),
                    hazmat)
                self.keys[kid] = certificate.public_key()
            cache_control = response.headers['Cache-Control']
            self.max_age = parse_cache_control_header(cache_control).max_age
            self.cached_at = now