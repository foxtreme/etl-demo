from unittest.mock import Mock
import pytest
from load import load_repositories


def test_load_repositories_executes_statement(repository_factory):
    session = Mock()
    repositories = [
        repository_factory(1),
        repository_factory(2),
        repository_factory(3)
    ]

    load_repositories(session, repositories, batch_size=500)
    session.execute.assert_called_once()


def test_load_repositories_creates_multiple_batches(repository_factory):
    session = Mock()

    repositories = [
        repository_factory(1),
        repository_factory(2),
        repository_factory(3),
        repository_factory(4),
        repository_factory(5)
    ]

    load_repositories(session, repositories, batch_size=2)
    assert session.execute.call_count == 3


def test_load_repositories_rejects_invalid_batch_size(repository_factory):
    session = Mock()
    repositories = [
        repository_factory(1),
    ]

    with pytest.raises(ValueError, match="batch_size must be > 0"):
        load_repositories(session, repositories, batch_size=0)

    session.execute.assert_not_called()
