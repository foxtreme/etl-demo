from extract import extract_repositories
from transform import transform_repository

repositories = extract_repositories(org="microsoft")

for repository in repositories:
    transformed_repository = transform_repository(repository)
    print(transformed_repository)
