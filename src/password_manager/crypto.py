import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import InvalidToken

from .exceptions import InvalidMasterPasswordError

KEY_LENGTH=32
SALT_SIZE=16
ITERATIONS=600_000

def generate_salt()->bytes:
    """generate a random salt for key derivation"""
    return os.urandom(SALT_SIZE)

class CryptoService:
    """encrypt and decrypt strings with a key derived from a master password"""
 
    def __init__(self,master_password:str,salt:bytes)->None:
        """initialize the crypto service with a master password and salt"""
        kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),length=KEY_LENGTH,salt=salt,iterations=ITERATIONS)
        key=kdf.derive(master_password.encode())
        fernet_key=base64.urlsafe_b64encode(key)
        self._fernet=Fernet(fernet_key)

    def encrypt(self,plaintext:str)->str:
        """encrypt a plaintext string and return a token as string"""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str) -> str:
        """decrypt a token back to plaintext"""
        try:
            return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken as e:
            raise InvalidMasterPasswordError() from e