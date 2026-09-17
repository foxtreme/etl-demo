import time
import requests


def request_with_retry(
        url: str,
        *,
        params=None,
        headers=None,
        timeout=10,
        max_retries=3,
        delay=1
):
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url,
                                    params=params,
                                    headers=headers,
                                    timeout=timeout
                                    )

        except (requests.Timeout, requests.ConnectionError):
            if attempt < max_retries:
                time.sleep(delay)
                continue
            raise
        if is_retryable_response(response):
            if attempt < max_retries:
                time.sleep(delay)
                continue

        response.raise_for_status()
        return response


def is_retryable_response(response: requests.Response) -> bool:
    return response.status_code == 429 or 500 <= response.status_code < 600
