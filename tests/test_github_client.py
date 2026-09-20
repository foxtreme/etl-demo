import github_client


def test_github_client_get_builds_request(monkeypatch):
    captured_request = {}

    class FakeResponse:
        pass

    def fake_request_with_retry(url, **kwargs):
        captured_request["url"] = url
        captured_request["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr(github_client, "request_with_retry", fake_request_with_retry)

    client = github_client.GitHubClient(
        token="test-token",
        timeout=15,
        max_retries=3,
        retry_delay=2.5
    )

    response = client.get(
        "https://api.github.com/test",
        params={"page": 2, "per_page": 50},
    )

    assert isinstance(response, FakeResponse)
    assert captured_request["url"] == "https://api.github.com/test"
    assert captured_request["kwargs"]["params"] == {"page": 2, "per_page": 50}

    assert captured_request["kwargs"]["headers"] == {"Authorization": "Bearer test-token",
                                                     "Accept": "application/vnd.github.v3+json"}
    assert captured_request["kwargs"]["timeout"] == 15
    assert captured_request["kwargs"]["max_retries"] == 3
    assert captured_request["kwargs"]["delay"] == 2.5
