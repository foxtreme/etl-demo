import pytest

from transform import transform_repository
from datetime import datetime


def test_transform_repository():
    github_repository = {
        "id": 12345,
        "name": "test-project",
        "full_name": "microsft/test-oroject",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "created_at": "2025-01-01T12:00:00Z",
        "updated_at": "2025-08-01T12:00:00Z"
    }

    repository = transform_repository(github_repository)

    assert repository.id == 12345
    assert repository.name == "test-project"
    assert repository.full_name == "microsft/test-oroject"
    assert repository.language == "Python"
    assert repository.stars == 100
    assert repository.forks == 20
    assert repository.open_issues == 5
    assert repository.created_at == datetime.fromisoformat("2025-01-01T12:00:00Z")
    assert repository.updated_at == datetime.fromisoformat("2025-08-01T12:00:00Z")


def test_transform_repository_without_language():
    github_repository = {
        "id": 12345,
        "name": "test-project",
        "full_name": "microsft/test-oroject",
        "language": None,
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "created_at": "2025-01-01T12:00:00Z",
        "updated_at": "2025-08-01T12:00:00Z"
    }

    repository = transform_repository(github_repository)

    assert repository.language is None


def test_transform_repository_with_missing_name():
    github_repository = {
        "id": 12345,
        "full_name": "microsft/test-oroject",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "created_at": "2025-01-01T12:00:00Z",
        "updated_at": "2025-08-01T12:00:00Z"
    }
    with pytest.raises(KeyError):
        transform_repository(github_repository)
