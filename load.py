import logging
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from models import Repository
from database_models import RepositoryDB

logger = logging.getLogger(__name__)


def load_repositories(session: Session, repositories: list[Repository], batch_size: int = 500) -> None:
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    for start in range(0, len(repositories), batch_size):
        batch = repositories[start:start + batch_size]
        logger.info(
            "Loading batch containing %d repositories",
            len(batch),
        )
        repository_data = [
            {
                "id": repository.id,
                "name": repository.name,
                "full_name": repository.full_name,
                "language": repository.language,
                "stars": repository.stars,
                "forks": repository.forks,
                "open_issues": repository.open_issues,
                "created_at": repository.created_at,
                "updated_at": repository.updated_at
            }
            for repository in batch
        ]

        stmt = insert(RepositoryDB).values(repository_data)

        stmt = stmt.on_conflict_do_update(
            index_elements=[RepositoryDB.id],
            set_={
                "name": stmt.excluded.name,
                "full_name": stmt.excluded.full_name,
                "language": stmt.excluded.language,
                "stars": stmt.excluded.stars,
                "forks": stmt.excluded.forks,
                "open_issues": stmt.excluded.open_issues,
                "created_at": stmt.excluded.created_at,
                "updated_at": stmt.excluded.updated_at
            },
        )
        session.execute(stmt)
    logger.info(
        "Prepared %d repositories for database loading",
        len(repositories),
    )
