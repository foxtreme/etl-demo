from sqlalchemy import select
from database import SessionLocal
from database_models import RepositoryDB
from load import load_repositories


def test_load_repository_inserts_into_database(db_session, repository_factory):
    repository = repository_factory(999999)
    load_repositories(db_session, [repository], batch_size=500)
    db_session.commit()
    result = db_session.execute(select(RepositoryDB).where(RepositoryDB.id == repository.id))
    saved_repository = result.scalar_one()

    assert saved_repository.id == repository.id
    assert saved_repository.name == repository.name
    assert saved_repository.full_name == repository.full_name
    assert saved_repository.language == repository.language
    assert saved_repository.stars == repository.stars


def test_load_repository_updates_existing_repository(db_session, repository_factory):
    repository = repository_factory(999998)

    load_repositories(db_session, [repository], batch_size=500)
    db_session.commit()
    repository.stars = 9999
    load_repositories(db_session, [repository], batch_size=500)
    db_session.commit()

    result = db_session.execute(select(RepositoryDB).where(RepositoryDB.id == repository.id))
    saved_repository = result.scalar_one()
    assert saved_repository.stars == 9999


def test_load_repositories_creates_multiple_batches(db_session, repository_factory):
    repositories = [
        repository_factory(999991),
        repository_factory(999992),
        repository_factory(999993),
        repository_factory(999994),
        repository_factory(999995)
    ]

    load_repositories(db_session, repositories, batch_size=2)
    db_session.commit()

    result = db_session.execute(
        select(RepositoryDB).where(
            RepositoryDB.id.in_(repository.id for repository in repositories)
        )
    )

    saved_repositories = result.scalars().all()
    assert len(saved_repositories) == 5
    saved_ids = {
        repository.id
        for repository in saved_repositories
    }

    expected_ids = {
        repository.id
        for repository in repositories
    }

    assert saved_ids == expected_ids


def test_load_repositories_rolls_back_on_failure(repository_factory):
    repositories = [
        repository_factory(999996),
        repository_factory(999997),
    ]
    with SessionLocal() as session:
        try:
            load_repositories(session, repositories, batch_size=2)
            raise RuntimeError("Simulated ETL failure")
        except RuntimeError:
            session.rollback()

    with SessionLocal() as session:
        result = session.execute(
            select(RepositoryDB).where(
                RepositoryDB.id.in_(
                    repository.id for repository in repositories
                )
            )
        )
        saved_repositories = result.scalars().all()
        assert saved_repositories == []
