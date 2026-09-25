"""Basic password strength checks for the master password"""

import string

MIN_LENGTH = 12


def check_password_strength(password: str) -> list[str]:
    """Return a list of warnings about weaknesses in the password"""
    warnings: list[str] = []

    if len(password) < MIN_LENGTH:
        warnings.append(f"Password is shorter than {MIN_LENGTH} characters")

    if not any(c.islower() for c in password):
        warnings.append("Missing a lowercase letter")

    if not any(c.isupper() for c in password):
        warnings.append("Missing an uppercase letter")

    if not any(c.isdigit() for c in password):
        warnings.append("Missing a digit")

    if not any(c in string.punctuation for c in password):
        warnings.append("Missing a symbol")

    return warnings