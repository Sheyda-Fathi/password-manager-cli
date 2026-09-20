"""Data models for the password manager"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self


def _utc_now() -> datetime:
    """return the current time as a timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)


@dataclass(repr=False)
class Entry:
    """A single saved credential"""

    site: str
    username: str
    password: str
    notes: str | None = None
    created_at: datetime = field(default_factory=_utc_now, compare=False)

    def __str__(self) -> str:
        return f"{self.site} ({self.username})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(site={self.site!r}, "
            f"username={self.username!r}, password='****')")

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-friendly dict"""
        return {
            "site": self.site,
            "username": self.username,
            "password": self.password,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build an Entry from a dict created by `to_dict`"""
        return cls(
                    site=data["site"],
                    username=data["username"],
                    password=data["password"],
                    notes=data.get("notes"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                )