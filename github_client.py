import requests

from request_utils import request_with_retry


class GitHubClient:

    def __init__(self, token: str, timeout: int, max_retries: int, retry_delay: float):
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get(self, url: str, *, params=None):
        headers = {"Authorization": f"Bearer {self.token}",
                   "Accept": "application/vnd.github.v3+json"}

        return request_with_retry(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout,
            max_retries=self.max_retries,
            delay=self.retry_delay,
        )
