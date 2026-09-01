def transform_repository(repository):
    return {
        "name": repository["name"],
        "language": repository["language"],
        "stars": repository["stargazers_count"],
        "forks": repository["forks_count"]
    }
