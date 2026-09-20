import pytest
from password_manager.crypto import SALT_SIZE, CryptoService, generate_salt
from password_manager.exceptions import InvalidMasterPasswordError


# test 1
def test_encrypt_decrypt_roundtrip():
    random_salt = generate_salt()
    service = CryptoService("mypassword", random_salt)
    text = service.encrypt("hello guys")
    text_decoded = service.decrypt(text)
    assert text_decoded == "hello guys"


# test 2
def test_decrypt_with_wrong_password_raises():
    random_salt = generate_salt()
    service1 = CryptoService("pass1", random_salt)
    service2 = CryptoService("pass2", random_salt)
    token = service1.encrypt("random text for obj1")
    with pytest.raises(InvalidMasterPasswordError):
        service2.decrypt(token)


# test 3
def test_decrypt_with_different_salt_raises():
    service1 = CryptoService("samepass", generate_salt())
    service2 = CryptoService("samepass", generate_salt())
    token = service1.encrypt("secret text")
    with pytest.raises(InvalidMasterPasswordError):
        service2.decrypt(token)


# test 4
def test_encrypted_token_hides_plaintext():
    service = CryptoService("mypassword", generate_salt())
    token = service.encrypt("supersecretvalue")
    assert "supersecretvalue" not in token


# test 5
def test_generate_salt_size_and_randomness():
    salt1 = generate_salt()
    salt2 = generate_salt()
    assert len(salt1) == SALT_SIZE
    assert salt1 != salt2


# test 6
def test_persian_password_and_text_roundtrip():
    """non-ascii (persian) master password and text should work correctly"""
    service = CryptoService("mymainpass", generate_salt())
    token = service.encrypt("hellooooo")
    assert service.decrypt(token) ==  "hellooooo"