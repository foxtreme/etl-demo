import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    raise RuntimeError("GITHUB_TOKEN environment variable not set")

response = requests.get("https://api.github.com/rate_limit",
                        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"},
                        timeout=10)
response.raise_for_status()

data = response.json()
print(data["rate"])
