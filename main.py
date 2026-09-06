import time

from database import SessionLocal
from extract import extract_repositories
from load import load_repositories
from transform import transform_repository

start_time = time.perf_counter()

repositories = [
    transform_repository(repository)
    for repository in extract_repositories(
        org="microsoft",
        per_page=100,
        max_pages=1
    )
]

print("Repositories extracted and transformed: {}".format(len(repositories)))

with SessionLocal() as session:
    try:
        load_repositories(session, repositories, batch_size=500)
        session.commit()

    except Exception:
        session.rollback()
        raise

elapsed_time = time.perf_counter() - start_time
print(f"Database load completed in: {elapsed_time:.4f} seconds")
