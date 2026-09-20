import extract


def test_extract_repositories_returns_repositories():
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

    class FakeGitHubClient:

        def get(self, url, *, params=None):
            class FakeResponse:
                def json(self):
                    return fake_repositories

            return FakeResponse()

    repositories = list(
        extract.extract_repositories(
            FakeGitHubClient(),
            org="test-org",
            max_pages=1
        )
    )

    assert repositories == fake_repositories


def test_extract_repositories_uses_correct_url_and_params():
    captured_request = {}

    class FakeResponse:

        def json(self):
            return []

    class FakeGitHubClient:
        def get(self, url, *, params=None):
            captured_request["url"] = url
            captured_request["params"] = params
            return FakeResponse()

    list(
        extract.extract_repositories(
            FakeGitHubClient(),
            org="test-org",
            page=3,
            per_page=50,
            max_pages=3
        )
    )

    assert captured_request["url"] == \
           "https://api.github.com/orgs/test-org/repos"

    assert captured_request["params"] == {
        "page": 3,
        "per_page": 50
    }


def test_extract_repositories_handles_multiple_pages():
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

        def json(self):
            return self.repositories

    class FakeGitHubClient:
        def get(self, url, *, params=None):
            page = params["page"]
            requested_pages.append(page)
            return FakeResponse(pages[page])

    repositories = list(
        extract.extract_repositories(
            FakeGitHubClient(),
            org="test-org",
            page=1,
            per_page=2,
            max_pages=2
        )
    )

    assert repositories == [
        {"id": 1, "name": "repo-one"},
        {"id": 2, "name": "repo-two"},
        {"id": 3, "name": "repo-three"},
        {"id": 4, "name": "repo-four"}
    ]

    assert requested_pages == [1, 2]


def test_extract_repositories_stops_on_empty_page():
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

        def json(self):
            return self.repositories

    class FakeGitHubClient:
        def get(self, url, *, params=None):
            page = params["page"]
            requested_pages.append(page)
            return FakeResponse(pages[page])

    repositories = list(
        extract.extract_repositories(
            FakeGitHubClient(),
            org="test-org",
            page=1,
            per_page=2,
            max_pages=3
        )
    )

    assert repositories == [
        {"id": 1, "name": "repo-one"},
        {"id": 2, "name": "repo-two"}
    ]

    assert requested_pages == [1, 2]
