"""The core vault that ties together crypto, storage, and models"""

import base64
import functools
from collections.abc import Iterator
from pathlib import Path

from .crypto import CryptoService, generate_salt
from .exceptions import (
    CorruptedVaultError,
    DuplicateEntryError,
    EntryNotFoundError,
    InvalidMasterPasswordError,
    VaultError,
)
from .models import Entry
from .storage import JSONStorage

CHECK_VALUE = "vault-check"


def require_unlocked(method):
    """Decorator: raise VaultError if the vault is locked"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self._unlocked:
            raise VaultError("Vault is locked.")
        return method(self, *args, **kwargs)

    return wrapper


class Vault:
    """Encrypted collection of password entries stored on disk"""

    def __init__(self, path: Path, crypto: CryptoService, salt: bytes) -> None:
        self._path = path
        self._storage = JSONStorage(path)
        self._crypto = crypto
        self._salt = salt
        self._entries: dict[str, Entry] = {}
        self._unlocked = False

    # construction

    @classmethod
    def init(cls, path: Path, master_password: str) -> "Vault":
        """Create a new empty vault at `path`"""
        storage = JSONStorage(path)
        if storage.exists():
            raise VaultError(f"Vault already exists at '{path}'.")

        salt = generate_salt()
        crypto = CryptoService(master_password, salt)
        vault = cls(path, crypto, salt)

        initial_data = {
            "version": 1,
            "salt": base64.urlsafe_b64encode(salt).decode("ascii"),
            "check": crypto.encrypt(CHECK_VALUE),
            "entries": [],
        }
        vault._storage.save(initial_data)
        vault._unlocked = True
        return vault

    @classmethod
    def open(cls, path: Path, master_password: str) -> "Vault":
        """Open an existing vault and decrypt its entries """
        storage = JSONStorage(path)
        data = storage.load()

        try:
            salt = base64.urlsafe_b64decode(data["salt"].encode("ascii"))
            check_token = data["check"]
            raw_entries = data["entries"]
        except (KeyError, TypeError, ValueError) as e:
            raise CorruptedVaultError("vault file is missing required fields") from e

        crypto = CryptoService(master_password, salt)

        if crypto.decrypt(check_token) != CHECK_VALUE:
            raise InvalidMasterPasswordError()

        vault = cls(path, crypto, salt)
        for entry_data in raw_entries:
            try:
                entry_data = dict(entry_data)
                entry_data["password"] = crypto.decrypt(entry_data["password"])
                if entry_data.get("notes") is not None:
                    entry_data["notes"] = crypto.decrypt(entry_data["notes"])
                entry = Entry.from_dict(entry_data)
            except InvalidMasterPasswordError:
                raise
            except (KeyError, TypeError, ValueError) as e:
                raise CorruptedVaultError("a vault entry is malformed") from e
            vault._entries[entry.site] = entry

        vault._unlocked = True
        return vault

    # context manager
    def __enter__(self) -> "Vault":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.save()
        self.lock()

    # public API
    @property
    def is_locked(self) -> bool:
        return not self._unlocked

    @require_unlocked
    def add(self, entry: Entry) -> None:
        if entry.site in self._entries:
            raise DuplicateEntryError(entry.site)
        self._entries[entry.site] = entry

    @require_unlocked
    def get(self, site: str) -> Entry:
        if site not in self._entries:
            raise EntryNotFoundError(site)
        return self._entries[site]

    @require_unlocked
    def update(self, entry: Entry) -> None:
        if entry.site not in self._entries:
            raise EntryNotFoundError(entry.site)
        self._entries[entry.site] = entry

    @require_unlocked
    def delete(self, site: str) -> None:
        if site not in self._entries:
            raise EntryNotFoundError(site)
        del self._entries[site]

    @require_unlocked
    def list_sites(self) -> list[str]:
        return list(self._entries.keys())

    @require_unlocked
    def search(self, keyword: str) -> Iterator[Entry]:
        """Yield entries whose site contains `keyword` (case-insensitive)"""
        keyword_lower = keyword.lower()
        for entry in self._entries.values():
            if keyword_lower in entry.site.lower():
                yield entry

    # persistence
    def save(self) -> None:
        """Encrypt entries and write the vault to disk"""
        encrypted_entries = []
        for entry in self._entries.values():
            entry_dict = entry.to_dict()
            entry_dict["password"] = self._crypto.encrypt(entry_dict["password"])
            if entry_dict.get("notes") is not None:
                entry_dict["notes"] = self._crypto.encrypt(entry_dict["notes"])
            encrypted_entries.append(entry_dict)

        data = {
            "version": 1,
            "salt": base64.urlsafe_b64encode(self._salt).decode("ascii"),
            "check": self._crypto.encrypt(CHECK_VALUE),
            "entries": encrypted_entries,
        }
        self._storage.save(data)

    def lock(self) -> None:
        """Clear decrypted entries from memory"""
        self._entries.clear()
        self._unlocked = False