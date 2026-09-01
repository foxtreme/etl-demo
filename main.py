from extract import extract_repositories
from transform import transform_repository

for repository in extract_repositories(org="microsoft", per_page=100, max_pages=1):
    transformed_repository = transform_repository(repository)
    print(transformed_repository)
    print(type(transformed_repository.created_at))
    print(type(transformed_repository.updated_at))
    break
