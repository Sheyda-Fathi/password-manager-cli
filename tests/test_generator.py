import pytest

from password_manager.generator import (
    DIGITS,
    LOWERCASE,
    SYMBOLS,
    UPPERCASE,
    generate_password,
)


def test_default_length_is_16():
    """The default password length should be 16"""
    pw = generate_password()
    assert len(pw) == 16


@pytest.mark.parametrize("length", [1, 8, 16, 32, 64])
def test_custom_length(length):
    """The password should have the requested length"""
    pw = generate_password(length=length)
    assert len(pw) == length


def test_length_zero_raises():
    """A length of 0 should raise ValueError"""
    with pytest.raises(ValueError):
        generate_password(length=0)


def test_negative_length_raises():
    """A negative length should raise ValueError"""
    with pytest.raises(ValueError):
        generate_password(length=-5)


def test_all_types_disabled_raises():
    """Disabling every character type should raise ValueError"""
    with pytest.raises(ValueError):
        generate_password(
            use_lowercase=False,
            use_uppercase=False,
            use_digits=False,
            use_symbols=False,
        )


def test_only_digits_when_others_disabled():
    """With only digits enabled, every character should be a digit"""
    pw = generate_password(
        length=50,
        use_lowercase=False,
        use_uppercase=False,
        use_digits=True,
        use_symbols=False,
    )
    assert all(c in DIGITS for c in pw)


def test_only_lowercase():
    """With only lowercase enabled, every character should be a-z"""
    pw = generate_password(
        length=50,
        use_lowercase=True,
        use_uppercase=False,
        use_digits=False,
        use_symbols=False,
    )
    assert all(c in LOWERCASE for c in pw)


def test_all_types_included():
    """With all types enabled, each type should appear in a long password"""
    pw = generate_password(length=200)
    assert any(c in LOWERCASE for c in pw)
    assert any(c in UPPERCASE for c in pw)
    assert any(c in DIGITS for c in pw)
    assert any(c in SYMBOLS for c in pw)


def test_two_passwords_differ():
    """Two generated passwords should not be equal"""
    assert generate_password() != generate_password()
