import json
import time
from datetime import timezone

import pytest
from password_manager.models import Entry


# test 1
def test_repr_masks_password():
    entry = Entry("github", "sheyda", "secret123")
    assert "secret123" not in repr(entry)
    assert "****" in repr(entry)


# test 2
def test_str_does_not_leak_password():
    entry = Entry("github", "sheyda", "secret123")
    assert "secret123" not in str(entry)


# test 3
def test_notes_default_is_none():
    entry = Entry("github", "sheyda", "secret123")
    assert entry.notes is None


# test 4
def test_created_at_differs_between_entries():
    a = Entry("a", "u", "p")
    time.sleep(0.01)
    b = Entry("b", "u", "p")
    assert a.created_at != b.created_at


# test 5
def test_created_at_is_utc_aware():
    entry = Entry("a", "u", "p")
    assert entry.created_at.tzinfo == timezone.utc


# test 6
def test_equality_ignores_created_at():
    a = Entry("github", "sheyda", "pw")
    time.sleep(0.01)
    b = Entry("github", "sheyda", "pw")
    assert a == b


# test 7
def test_to_dict_from_dict_roundtrip():
    original = Entry("github", "sheyda", "pw", notes="work account")
    restored = Entry.from_dict(original.to_dict())
    assert restored == original
    assert restored.created_at == original.created_at


# test 8
def test_to_dict_is_json_serializable():
    entry = Entry("github", "sheyda", "pw")
    text = json.dumps(entry.to_dict())
    assert "github" in text


# test 9
def test_from_dict_missing_field_raises_key_error():
    with pytest.raises(KeyError):
        Entry.from_dict({"site": "github"})