"""Secure random password generation."""

import secrets

LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?~|/"


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a cryptographically secure random password.

    Args:
        length: Number of characters in the password (must be >= 1)
        use_uppercase: Include A-Z if True
        use_lowercase: Include a-z if True
        use_digits: Include 0-9 if True
        use_symbols: Include punctuation if True

    Returns:
        A random password string

    Raises:
        ValueError: If length < 1 or no character type is enabled
    """
    if length < 1:
        raise ValueError("Password length must be at least 1")

    chars = ""
    if use_lowercase:
        chars += LOWERCASE
    if use_uppercase:
        chars += UPPERCASE
    if use_digits:
        chars += DIGITS
    if use_symbols:
        chars += SYMBOLS

    if not chars:
        raise ValueError("At least one character type must be enabled")

    return "".join(secrets.choice(chars) for _ in range(length))
