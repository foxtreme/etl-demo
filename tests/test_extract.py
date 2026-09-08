import pytest
import requests
import extract


def test_extract_repositories_returns_repositories(monkeypatch):
    fake_repositories = [
        {
            "id": 1,
            "name": "repo-one",
            "full_name": "test_org/repo-one",
        },
        {
            "id": 2,
            "name": "repo-two",
            "full_name": "test_org/repo-two",
        }
    ]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_repositories

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(extract.requests, "get", fake_get)

    repositories = list(extract.extract_repositories(org="test-org", max_pages=1))
    assert repositories == fake_repositories


def test_extract_repositories_uses_correct_url_and_params(monkeypatch):
    captured_request = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    def fake_get(url, **kwargs):
        captured_request["url"] = url
        captured_request["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr(extract.requests, "get", fake_get)

    list(extract.extract_repositories(org="test-org", page=3, per_page=50, max_pages=3))

    assert captured_request["url"] == "https://api.github.com/orgs/test-org/repos"
    assert captured_request["kwargs"]["params"] == {"page": 3, "per_page": 50}


def test_extract_repositories_handles_multiple_pages(monkeypatch):
    pages = {
        1: [
            {"id": 1, "name": "repo-one"},
            {"id": 2, "name": "repo-two"},
        ],
        2: [
            {"id": 3, "name": "repo-three"},
            {"id": 4, "name": "repo-four"}
        ]
    }

    requested_pages = []

    class FakeResponse:

        def __init__(self, repositories):
            self.repositories = repositories

        def raise_for_status(self):
            pass

        def json(self):
            return self.repositories

    def fake_get(url, **kwargs):
        page = kwargs["params"]["page"]
        requested_pages.append(page)

        return FakeResponse(pages[page])

    monkeypatch.setattr(extract.requests, "get", fake_get)

    repositories = list(extract.extract_repositories(org="test-org", page=1, per_page=2, max_pages=2))

    assert repositories == [
        {"id": 1, "name": "repo-one"},
        {"id": 2, "name": "repo-two"},
        {"id": 3, "name": "repo-three"},
        {"id": 4, "name": "repo-four"}
    ]

    assert requested_pages == [1, 2]


def test_extract_repositories_stops_on_empty_page(monkeypatch):
    pages = {
        1: [
            {"id": 1, "name": "repo-one"},
            {"id": 2, "name": "repo-two"}
        ],
        2: [],
        3: [
            {"id": 3, "name": "repo-three"}
        ]
    }

    requested_pages = []

    class FakeResponse:

        def __init__(self, repositories):
            self.repositories = repositories

        def raise_for_status(self):
            pass

        def json(self):
            return self.repositories

    def fake_get(url, **kwargs):
        page = kwargs["params"]["page"]
        requested_pages.append(page)
        return FakeResponse(pages[page])

    monkeypatch.setattr(extract.requests, "get", fake_get)

    repositories = list(extract.extract_repositories(org="test-org", page=1, per_page=2, max_pages=3))

    assert repositories == [
        {"id": 1, "name": "repo-one"},
        {"id": 2, "name": "repo-two"}
    ]

    assert requested_pages == [1, 2]


def test_extract_repositories_propagates_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise requests.HTTPError("Github returned an error")

        def json(self):
            return []

    def fake_get(url, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(extract.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        list(extract.extract_repositories(org="test-org", max_pages=1))
