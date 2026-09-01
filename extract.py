import requests


def extract_repositories(org: str, page: int = 1, per_page: int = 100, max_pages: int = 100):
    while page <= max_pages:
        response = requests.get(
            f"https://api.github.com/orgs/{org}/repos",
            params={"page": page, "per_page": per_page},
            timeout=10
        )
        response.raise_for_status()
        repos = response.json()

        if not repos:
            break

        for repo in repos:
            yield repo
        page += 1
