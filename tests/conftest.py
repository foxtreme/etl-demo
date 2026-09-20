from datetime import datetime
import pytest
from database import Database
from config import Settings
from models import Repository
from database_models import RepositoryDB
from sqlalchemy import delete


@pytest.fixture(scope="session")
def database():
    settings = Settings()
    return Database(settings.database_url)


@pytest.fixture
def db_session(database):
    with database.session_factory() as session:
        yield session


@pytest.fixture
def repository_factory(register_repository_cleanup):
    def create_repository(
            repository_id: int, *, stars: int = 100, language: str | None = "Python"
    ) -> Repository:
        register_repository_cleanup(repository_id)

        return Repository(
            id=repository_id,
            name="test-repo-{}".format(repository_id),
            full_name="test-org/test-repo-{}".format(repository_id),
            language=language,
            stars=stars,
            forks=20,
            open_issues=5,
            created_at=datetime.fromisoformat("2025-01-01T12:00:00Z"),
            updated_at=datetime.fromisoformat("2025-08-01T12:00:00Z")
        )

    return create_repository


@pytest.fixture
def register_repository_cleanup(db_session):
    repository_ids = set()

    def register(*ids):
        repository_ids.update(ids)

    yield register

    db_session.rollback()

    if repository_ids:
        stmt = delete(RepositoryDB).where(RepositoryDB.id.in_(repository_ids))
        db_session.execute(stmt)
        db_session.commit()
