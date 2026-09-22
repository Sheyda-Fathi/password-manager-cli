import json
import os
from pathlib import Path

from .exceptions import CorruptedVaultError, VaultNotFoundError

DEFAULT_ENCODING = "utf-8"


class JSONStorage:
    """Read and write JSON files with atomic writes."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def exists(self) -> bool:
        """Return True if the storage file exists on disk."""
        return self._path.exists()

    def save(self, data: dict) -> None:
        """Write data to disk atomically."""
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        try:
            with open(tmp_path, "w", encoding=DEFAULT_ENCODING) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self._path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    def load(self) -> dict:
        """Read the JSON file and return its content as a dict.

        Raises:
            VaultNotFoundError: if the file does not exist.
            CorruptedVaultError: if the file is not valid JSON, or is missing
                required fields.
        """
        if not self._path.exists():
            raise VaultNotFoundError(str(self._path))

        try:
            with open(self._path, "r", encoding=DEFAULT_ENCODING) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CorruptedVaultError("File is not valid JSON") from e

        if not isinstance(data, dict):
            raise CorruptedVaultError("File content is not a JSON object")
        if "version" not in data:
            raise CorruptedVaultError("File is missing the 'version' field")

        return data