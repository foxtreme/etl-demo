from sqlalchemy.orm import Session

from models import Repository
from database_models import RepositoryDB


def load_repository(session: Session, repository: Repository) -> None:
    repository_db = RepositoryDB(
        id=repository.id,
        name=repository.name,
        full_name=repository.full_name,
        language=repository.language,
        stars=repository.stars,
        forks=repository.forks,
        open_issues=repository.open_issues,
        created_at=repository.created_at,
        updated_at=repository.updated_at
    )

    session.add(repository_db)
    session.commit()
