import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(autouse=True)
def mock_db_name(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("arya_backend.config.MONGO_DB_NAME", "TEST_DB_")
