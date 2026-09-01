import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN environment variable not set")


def extract_repositories(org: str, page: int = 1, per_page: int = 100, max_pages: int = 20):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    while page <= max_pages:
        print(f"Fetching page {page}...")
        response = requests.get(
            f"https://api.github.com/orgs/{org}/repos",
            params={"page": page, "per_page": per_page},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        repos = response.json()

        if not repos:
            break

        for repo in repos:
            yield repo
        page += 1
