import pytest
from pydantic import ValidationError
from config import Settings


def test_settings_load_from_environment(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/testdb")

    settings = Settings()
    assert settings.github_token == "test-token"
    assert settings.database_url == "postgresql+psycopg://user:password@localhost:5432/testdb"


def test_settings_use_defaults(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/testdb")

    monkeypatch.delenv("REQUEST_TIMEOUT", raising=False)
    monkeypatch.delenv("MAX_RETRIES", raising=False)
    monkeypatch.delenv("RETRY_DELAY", raising=False)
    
    settings = Settings(_env_file=None)
    assert settings.request_timeout == 10
    assert settings.max_retries == 3
    assert settings.retry_delay == 1


def test_settings_convert_environment_values(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/testdb")
    monkeypatch.setenv("REQUEST_TIMEOUT", "20")
    monkeypatch.setenv("MAX_RETRIES", "5")
    monkeypatch.setenv("RETRY_DELAY", "2.5")

    settings = Settings()

    assert settings.request_timeout == 20
    assert isinstance(settings.request_timeout, int)

    assert settings.max_retries == 5
    assert isinstance(settings.max_retries, int)

    assert settings.retry_delay == 2.5
    assert isinstance(settings.retry_delay, float)


def test_settings_require_github_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/testdb")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_require_database_url(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_invalid_timeout(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/testdb")
    monkeypatch.setenv("REQUEST_TIMEOUT", "0")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_reject_negative_retries(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/testdb")
    monkeypatch.setenv("MAX_RETRIES", "-1")

    with pytest.raises(ValidationError):
        Settings()
