from models import Repository


def transform_repository(repository: dict) -> Repository:
    return Repository(
        id=repository["id"],
        name=repository["name"],
        full_name=repository["full_name"],
        language=repository["language"],
        stars=repository["stargazers_count"],
        forks=repository["forks_count"],
        open_issues=repository["open_issues_count"],
        created_at=repository["created_at"],
        updated_at=repository["updated_at"]
    )
