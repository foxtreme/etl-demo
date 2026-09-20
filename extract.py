import logging

logger = logging.getLogger(__name__)


def extract_repositories(github_client, org: str, *,
                         page: int = 1, per_page: int = 100, max_pages: int = 20):
    while page <= max_pages:
        logger.info("Fetching page %d", page)
        response = github_client.get(
            f"https://api.github.com/orgs/{org}/repos",
            params={"page": page, "per_page": per_page},
        )
        repos = response.json()

        if not repos:
            logger.info("No repositories returned on page %d; extraction complete", page)
            break

        for repo in repos:
            yield repo
        page += 1
