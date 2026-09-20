import pytest
from password_manager.exceptions import (
    CorruptedVaultError,
    DuplicateEntryError,
    EntryNotFoundError,
    InvalidMasterPasswordError,
    VaultError,
)


# test 1
def test_all_errors_are_vault_errors():
    errors = [
        InvalidMasterPasswordError(),
        CorruptedVaultError(),
        EntryNotFoundError("github"),
        DuplicateEntryError("github"),
    ]
    for error in errors:
        assert isinstance(error, VaultError)


# test 2
def test_entry_not_found_keeps_site_and_message():
    error = EntryNotFoundError("github")
    assert error.site == "github"
    assert "github" in str(error)
    assert "not found" in str(error)


# test 3
def test_duplicate_entry_keeps_site_and_message():
    error = DuplicateEntryError("github")
    assert error.site == "github"
    assert "github" in str(error)
    assert "already exists" in str(error)


# test 4
def test_default_messages():
    assert "master password" in str(InvalidMasterPasswordError())
    assert "corrupted" in str(CorruptedVaultError())


# test 5
def test_vault_error_catches_specific_errors():
    with pytest.raises(VaultError):
        raise InvalidMasterPasswordError()
    with pytest.raises(VaultError):
        raise EntryNotFoundError("github")