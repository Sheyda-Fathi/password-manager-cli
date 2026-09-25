from password_manager.strength import check_password_strength


def test_strong_password_has_no_warnings():
    """A password with all four character types and enough length passes clean"""
    assert check_password_strength("Str0ng!Pass1234") == []


def test_short_password_warns_about_length():
    """A password under 12 characters should warn about length"""
    warnings = check_password_strength("Ab1!")
    assert any("shorter than" in w for w in warnings)


def test_password_without_digit_warns():
    """A password with no digit should warn about the missing digit"""
    warnings = check_password_strength("NoDigitsHere!!")
    assert any("digit" in w for w in warnings)


def test_password_without_symbol_warns():
    """A password with no symbol should warn about the missing symbol"""
    warnings = check_password_strength("NoSymbolsHere1234")
    assert any("symbol" in w for w in warnings)


def test_password_without_uppercase_warns():
    """A password with no uppercase letter should warn about it"""
    warnings = check_password_strength("nouppercase123!")
    assert any("uppercase" in w for w in warnings)


def test_password_without_lowercase_warns():
    """A password with no lowercase letter should warn about it"""
    warnings = check_password_strength("NOLOWERCASE123!")
    assert any("lowercase" in w for w in warnings)