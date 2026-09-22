import pytest

from password_manager.exceptions import (
    DuplicateEntryError,
    EntryNotFoundError,
    InvalidMasterPasswordError,
    VaultError,
)
from password_manager.models import Entry
from password_manager.vault import Vault

#   init


def test_init_creates_vault_file(tmp_path):
    """After init, the vault file should exist on disk"""
    path = tmp_path / "test.vault"
    Vault.init(path, "mypass")
    assert path.exists()


def test_init_existing_vault_raises(tmp_path):
    """Initializing over an existing vault should raise VaultError"""
    path = tmp_path / "test.vault"
    Vault.init(path, "mypass")
    with pytest.raises(VaultError):
        Vault.init(path, "mypass")


#   open


def test_open_with_wrong_password_raises(tmp_path):
    """Opening with a wrong master password should raise InvalidMasterPasswordError"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "correct")
    v.add(Entry("github", "sheyda", "pw"))
    v.save()
    v.lock()

    with pytest.raises(InvalidMasterPasswordError):
        Vault.open(path, "wrong")


#   add / get


def test_add_then_get(tmp_path):
    """Adding an entry and getting it should return the same entry"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    entry = Entry("github", "sheyda", "secret")
    v.add(entry)

    result = v.get("github")
    assert result.site == "github"
    assert result.username == "sheyda"
    assert result.password == "secret"


def test_add_duplicate_raises(tmp_path):
    """Adding an entry for an existing site should raise DuplicateEntryError"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("github", "sheyda", "pw1"))
    with pytest.raises(DuplicateEntryError):
        v.add(Entry("github", "other", "pw2"))


def test_get_missing_raises(tmp_path):
    """Getting a non-existent site should raise EntryNotFoundError"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    with pytest.raises(EntryNotFoundError):
        v.get("github")


#   update / delete


def test_update_replaces_entry(tmp_path):
    """Updating an entry should replace its values"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("github", "sheyda", "old"))
    v.update(Entry("github", "sheyda", "new"))
    assert v.get("github").password == "new"


def test_update_missing_raises(tmp_path):
    """Updating a non-existent site should raise EntryNotFoundError"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    with pytest.raises(EntryNotFoundError):
        v.update(Entry("github", "sheyda", "pw"))


def test_delete_removes_entry(tmp_path):
    """Deleting an entry should remove it"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("github", "sheyda", "pw"))
    v.delete("github")
    with pytest.raises(EntryNotFoundError):
        v.get("github")


def test_delete_missing_raises(tmp_path):
    """Deleting a non-existent site should raise EntryNotFoundError"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    with pytest.raises(EntryNotFoundError):
        v.delete("github")


#   list / search


def test_list_sites(tmp_path):
    """list_sites should return every site added"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("github", "u", "p"))
    v.add(Entry("gmail", "u", "p"))
    assert set(v.list_sites()) == {"github", "gmail"}


def test_search_is_case_insensitive(tmp_path):
    """search should match sites case-insensitively"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("GitHub", "u", "p"))
    v.add(Entry("gmail", "u", "p"))

    results = list(v.search("git"))
    assert len(results) == 1
    assert results[0].site == "GitHub"


#   persistence


def test_save_and_reopen_roundtrip(tmp_path):
    """A saved entry should be recoverable after reopening with the password"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("github", "sheyda", "secret", notes="work"))
    v.save()
    v.lock()

    v2 = Vault.open(path, "mypass")
    entry = v2.get("github")
    assert entry.password == "secret"
    assert entry.notes == "work"


def test_context_manager_saves_and_locks(tmp_path):
    """Leaving the `with` block should save and lock the vault"""
    path = tmp_path / "test.vault"
    with Vault.init(path, "mypass") as v:
        v.add(Entry("github", "sheyda", "secret"))

    v2 = Vault.open(path, "mypass")
    assert v2.get("github").password == "secret"


#   locked behavior


def test_locked_vault_blocks_operations(tmp_path):
    """After lock, methods should raise VaultError"""
    path = tmp_path / "test.vault"
    v = Vault.init(path, "mypass")
    v.add(Entry("github", "sheyda", "pw"))
    v.lock()

    with pytest.raises(VaultError):
        v.get("github")
    with pytest.raises(VaultError):
        v.add(Entry("gmail", "u", "p"))
