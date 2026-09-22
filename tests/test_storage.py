import pytest

from password_manager.exceptions import CorruptedVaultError, VaultNotFoundError
from password_manager.storage import JSONStorage


def test_save_and_load_roundtrip(tmp_path):
    """Save then load should return the same data."""
    storage = JSONStorage(tmp_path / "test.vault")
    data = {"version": 1, "entries": []}

    storage.save(data)
    result = storage.load()

    assert result == data


def test_load_missing_file_raises_vault_not_found(tmp_path):
    """Loading a non-existent file should raise VaultNotFoundError."""
    storage = JSONStorage(tmp_path / "missing.vault")

    with pytest.raises(VaultNotFoundError):
        storage.load()


def test_load_invalid_json_raises_corrupted(tmp_path):
    """Loading a file with invalid JSON should raise CorruptedVaultError."""
    path = tmp_path / "bad.vault"
    path.write_text("not json", encoding="utf-8")
    storage = JSONStorage(path)

    with pytest.raises(CorruptedVaultError):
        storage.load()


def test_load_missing_version_raises_corrupted(tmp_path):
    """Loading a file without 'version' should raise CorruptedVaultError."""
    path = tmp_path / "noversion.vault"
    path.write_text('{"foo": "bar"}', encoding="utf-8")
    storage = JSONStorage(path)

    with pytest.raises(CorruptedVaultError):
        storage.load()


def test_save_leaves_no_tmp_file(tmp_path):
    """After a successful save, no .tmp file should remain."""
    storage = JSONStorage(tmp_path / "test.vault")

    storage.save({"version": 1})

    assert list(tmp_path.glob("*.tmp")) == []
