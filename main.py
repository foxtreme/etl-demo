from database import SessionLocal
from extract import extract_repositories
from load import load_repository
from transform import transform_repository

with SessionLocal() as session:
    for repository in extract_repositories(
            org="microsoft",
            per_page=100,
            max_pages=1,
    ):
        transformed_repository = transform_repository(repository)
        load_repository(session, transformed_repository)
        print(f"Loaded: {transformed_repository.full_name}")
        break
