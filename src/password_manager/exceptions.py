"""custom exceptions for the password manager"""

class VaultError(Exception):
    """base class for all vault-related errors"""

class InvalidMasterPasswordError(VaultError):
    """when the master password is incorrect"""

    def __init__(self, message: str = "master password is incorrect") -> None:
        super().__init__(message)

class CorruptedVaultError(VaultError):
    """when the vault file is corrupted or unreadable"""

    def __init__(self, message: str = "vault file is corrupted or unreadable") -> None:
        super().__init__(message)

class EntryNotFoundError(VaultError):
    """when an entry for the given site does not exist"""

    def __init__(self, site: str) -> None:
        self.site = site
        super().__init__(f"entry for '{site}' not found")

class DuplicateEntryError(VaultError):
    """when trying to add an entry that already exists"""

    def __init__(self, site: str) -> None:
        self.site = site
        super().__init__(f"entry for '{site}' already exists")

class VaultNotFoundError(VaultError):
    """when the vault file does not exist yet"""
    
    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"vault not found at '{path}'.")