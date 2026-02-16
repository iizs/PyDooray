# [SPEC] PyDooray - Test Refactoring

**Status:** Draft
**Author:** Tech Lead (Tony)
**Date:** 2026-02-16
**Target Component:** `tests/`

## 1. Overview

The current test suite has two problems: (1) almost no unit tests — only `test_MessengerHookAttachments` runs without external services, and (2) integration tests are monolithic and hard to maintain. This spec defines a refactoring plan that adds a mock-based unit test layer, restructures integration tests, and ensures recent P0 fixes are properly tested.

### Goals
- Add unit test coverage for all public API methods using HTTP mocking
- Refactor monolithic integration tests into focused, independent test methods
- Cover P0/P1 fixes: `tag_ids` mapping, `MessengerHook.send()` return value, `get_members()` auto-inject
- Maintain existing integration tests as a separate tier

### Non-Goals
- Testing Dooray API correctness (that's Dooray's responsibility)
- Achieving 100% line coverage (focus on public interface coverage)
- Changing production code (test-only changes)

---

## 2. Data Model (Schema & Types)

### 2.1 Test Fixture: JSON Response Templates

Reusable JSON response dicts matching Dooray API response structure, stored in `tests/fixtures/`.

**File:** `tests/fixtures/responses.py`

```python
"""Reusable Dooray API response fixtures for unit tests."""

RESPONSE_HEADER_SUCCESS: dict = {
    "header": {
        "isSuccessful": True,
        "resultCode": 0,
        "resultMessage": "success"
    }
}

MEMBER_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [
        {
            "id": "1234567890",
            "name": "Test User",
            "userCode": "testuser",
            "externalEmailAddress": "test@example.com"
        }
    ],
    "totalCount": 1
}

PROJECT_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "9999999999",
        "code": "test-project",
        "description": "Test project",
        "scope": "private"
    }
}

RELATION_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "5555555555"
    }
}

WORKFLOW_LIST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [
        {"id": "wf-1", "name": "Registered", "class": "registered"},
        {"id": "wf-2", "name": "Working", "class": "working"},
        {"id": "wf-3", "name": "Closed", "class": "closed"}
    ],
    "totalCount": 3
}

MILESTONE_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "ms-1",
        "name": "v1.0",
        "status": "open",
        "startedAt": "2026-01-01T00:00:00Z",
        "endedAt": "2026-06-30T00:00:00Z"
    }
}

TAG_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "tag-1",
        "name": "bug",
        "color": "ff0000"
    }
}

POST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "post-1",
        "number": 1,
        "subject": "Test Post",
        "body": {"mimeType": "text/x-markdown", "content": "body"},
        "users": {
            "from": None,
            "to": [{"type": "member", "member": {"organizationMemberId": "1234567890"}}],
            "cc": []
        },
        "priority": "normal"
    }
}

POST_LIST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [POST_RESPONSE["result"]],
    "totalCount": 1
}

POST_LOG_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "log-1",
        "post": {"id": "post-1"},
        "type": "comment",
        "subtype": "general",
        "createdAt": "2026-01-01T00:00:00Z",
        "creator": {"type": "member", "member": {"organizationMemberId": "1234567890"}},
        "body": {"mimeType": "text/x-markdown", "content": "comment"}
    }
}

CHANNEL_LIST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [
        {
            "id": "ch-1",
            "title": "Test Channel",
            "organization": {"id": "org-1"},
            "type": "private",
            "users": {"participants": [{"type": "member", "member": {"organizationMemberId": "1234567890"}}]},
            "me": {"type": "member", "member": {"organizationMemberId": "1234567890"}, "role": "admin"},
            "capacity": 100,
            "status": "normal",
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:00:00Z",
            "archivedAt": None,
            "displayed": True
        }
    ],
    "totalCount": 1
}

INCOMING_HOOK_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "hook-1",
        "name": "Test Hook",
        "serviceType": "messenger",
        "url": "https://hook.dooray.com/test",
        "projects": [{"id": "9999999999"}]
    }
}
```

---

## 3. Interface Design (API / Signatures)

### 3.1 Test File Structure

```
tests/
├── __init__.py
├── conftest.py                      # Existing, keep as-is
├── tokens.py                        # Existing, keep as-is (git skip-worktree)
├── fixtures/
│   ├── __init__.py
│   └── responses.py                 # JSON response templates (Section 2.1)
├── unit/                            # NEW: mock-based unit tests
│   ├── __init__.py
│   ├── test_dooray_common.py        # Dooray (get_members, get_incoming_hook)
│   ├── test_dooray_messenger.py     # DoorayMessenger (all 6 methods)
│   ├── test_dooray_project.py       # DoorayProject (all methods)
│   ├── test_messenger_hook.py       # MessengerHook.send() return value
│   ├── test_messenger_hook_attachments.py  # MOVE from tests/ (already unit)
│   ├── test_post_builder.py         # PostBuilder fluent API
│   └── test_template_builder.py     # TemplateBuilder fluent API
└── integration/                     # MOVE existing integration tests
    ├── __init__.py
    ├── test_dooray_project.py       # Refactored from test_DoorayProject.py
    ├── test_messenger_hook.py       # MOVE from tests/ (rename)
    └── conftest.py                  # Integration-specific fixtures
```

### 3.2 pytest Configuration Update

**File:** `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py

# Run only unit tests by default (no API token needed)
# Use `pytest tests/integration` to run integration tests
markers =
    integration: marks tests as integration tests (require API token)
```

---

## 4. Internal Component Design (Class/Module Structure)

### 4.1 Unit Test Base Pattern

All unit tests use `unittest.mock.patch` to mock `requests.request` (for `DoorayBase._request`) or `requests.post` (for `MessengerHook.send`).

```python
# Common pattern for all Dooray API unit tests
from unittest.mock import patch, MagicMock
import dooray
from tests.fixtures.responses import MEMBER_RESPONSE

class TestDoorayCommon(unittest.TestCase):
    def setUp(self):
        self._dooray = dooray.Dooray(token="test-token")

    @patch("requests.request")
    def test_get_members_no_filter(self, mock_request):
        """Verify get_members() auto-injects name='' when no filters given."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = ""
        mock_resp.json.return_value = MEMBER_RESPONSE
        mock_request.return_value = mock_resp

        result = self._dooray.get_members()

        # Verify name='' was injected
        call_kwargs = mock_request.call_args
        self.assertIn("name", call_kwargs.kwargs["params"])
        self.assertEqual(call_kwargs.kwargs["params"]["name"], "")
```

### 4.2 Unit Test Classes

#### `tests/unit/test_dooray_common.py`

| Test Method | Validates |
|---|---|
| `test_get_members_no_filter` | Auto-injects `name=''` when no filter params given |
| `test_get_members_with_name` | Does NOT inject `name=''` when `name` is provided |
| `test_get_members_with_user_code` | Does NOT inject when `user_code` is provided |
| `test_get_members_with_external_emails_str` | Passes string directly |
| `test_get_members_with_external_emails_list` | Joins list with commas |
| `test_get_members_pagination` | Passes `page` and `size` params |
| `test_get_incoming_hook` | Correct endpoint and response parsing |

#### `tests/unit/test_dooray_messenger.py`

| Test Method | Validates |
|---|---|
| `test_get_channels` | Endpoint, unpaginated response (size=None) |
| `test_send_direct_message` | Correct body payload |
| `test_send_channel_message` | Correct endpoint with channel_id |
| `test_send_channel_log_alias` | Delegates to `send_channel_message` |
| `test_join_channel_single_member` | str → list normalization |
| `test_join_channel_multiple_members` | list passed directly |
| `test_leave_channel` | Correct endpoint and payload |
| `test_create_channel` | All params (title, member_ids, id_type, channel_type, capacity) |

#### `tests/unit/test_dooray_project.py`

| Test Method | Validates |
|---|---|
| `test_is_creatable_true` | Returns `True` on 200 |
| `test_is_creatable_false` | Returns `False` on `BadHttpResponseStatusCode` |
| `test_create_project` | Correct body (code, description, scope) |
| `test_get_project` | Endpoint and Project parsing |
| `test_get_workflows` | List response of Workflow |
| `test_create_email_address` | Body (emailAddress, name) |
| `test_get_email_address` | Endpoint with email_address_id |
| `test_create_tag` | Body (name, color), assertion on None |
| `test_get_tag` | Endpoint with tag_id |
| `test_create_milestone` | Body (name, startedAt, endedAt) |
| `test_get_milestones_with_status` | Query params include status |
| `test_get_milestone` | Endpoint with milestone_id |
| `test_update_milestone` | PUT body (name, status, startedAt, endedAt) |
| `test_delete_milestone` | DELETE method used |
| `test_create_hook` | Body (url, sendEvents) |
| `test_add_member` | Body (organizationMemberId, role) |
| `test_get_member` | Endpoint with member_id |
| `test_get_member_group` | Endpoint with member_group_id |
| `test_create_template` | Calls `to_json_dict()` on template object |
| `test_get_templates` | Pagination params |
| `test_get_template_with_interpolation` | Query param `interpolation=true` |
| `test_update_template` | PUT with `to_json_dict()` |
| `test_delete_template` | DELETE method used |
| `test_create_post` | Calls `to_json_dict()` on post object |
| `test_get_posts_tag_ids_mapping` | **P0: `tag_ids` maps to `tagIds` (not `ccMemberIds`)** |
| `test_get_posts_filter_params` | All 12 filter params mapped correctly |
| `test_get_post` | Endpoint with post_id |
| `test_update_post` | PUT with `to_json_dict()` |
| `test_set_post_workflow_for_member` | Endpoint with member_id, body with workflowId |
| `test_set_post_workflow` | POST set-workflow endpoint |
| `test_set_post_as_done` | POST set-done endpoint |
| `test_create_post_log` | Body with mimeType=text/x-markdown |
| `test_get_post_logs` | Pagination and order params |
| `test_get_post_log` | Endpoint with log_id |
| `test_update_post_log` | PUT body with content |
| `test_delete_post_log` | DELETE method used |

#### `tests/unit/test_messenger_hook.py`

| Test Method | Validates |
|---|---|
| `test_send_returns_true_on_success` | **P0: returns `True` when status_code == 200** |
| `test_send_returns_false_on_failure` | **P0: returns `False` when status_code != 200** |
| `test_send_payload_structure` | Correct JSON body (botName, botIconImage, text) |
| `test_send_with_attachments` | `attachments` key included when provided |
| `test_send_without_attachments` | `attachments` key absent when None |
| `test_constructor_assertions` | Validates assertion errors on invalid params |

#### `tests/unit/test_post_builder.py`

| Test Method | Validates |
|---|---|
| `test_minimal_post` | subject + body only |
| `test_full_post` | All fields set |
| `test_add_to_member` | PostUsers.to populated correctly |
| `test_add_to_email_user` | emailUser type with emailAddress + name |
| `test_add_cc_member` | PostUsers.cc populated |
| `test_add_cc_email_user` | emailUser in cc |
| `test_add_multiple_tags` | tag_ids accumulate |
| `test_to_json_dict_camel_case` | Output keys are camelCase |
| `test_to_json_dict_omits_none` | None fields excluded |

#### `tests/unit/test_template_builder.py`

| Test Method | Validates |
|---|---|
| `test_minimal_template` | templateName is always included |
| `test_full_template` | All fields set |
| `test_set_guide` | guide → PostBody with markdown mimeType |
| `test_set_is_default` | isDefault boolean |
| `test_to_json_dict_camel_case` | Output keys are camelCase |

#### `tests/unit/test_messenger_hook_attachments.py`

MOVE existing `tests/test_MessengerHookAttachments.py` as-is. No changes needed.

### 4.3 Integration Test Refactoring

**File:** `tests/integration/test_dooray_project.py`

Refactor the existing monolithic `TestDoorayProject` class. The key change: split `test_ProjectPost` (which covers Post CRUD + Workflow + Post Logs) into focused methods.

| Old Method | New Methods |
|---|---|
| `test_Project` | `test_project_get`, `test_project_is_creatable` |
| `test_ProjectMilestone` | `test_milestone_lifecycle` (keep as-is, already reasonable) |
| `test_ProjectMember` | `test_member_add_and_get` (keep as-is) |
| `test_ProjectMemberGroup` | `test_member_group_get` (keep as-is) |
| `test_ProjectTemplate` | `test_template_lifecycle` (keep as-is, already reasonable) |
| `test_ProjectPost` | Split into: |
| | `test_post_create_and_get` |
| | `test_post_update` |
| | `test_post_filter_by_to_member` |
| | `test_post_workflow_operations` |
| | `test_post_log_lifecycle` |

All integration test classes and methods must be decorated with `@pytest.mark.integration`.

**File:** `tests/integration/conftest.py`

```python
"""Integration test configuration. Requires valid API token."""
import pytest
import dooray
from tests.tokens import API_TOKEN

@pytest.fixture
def dooray_client():
    return dooray.Dooray(API_TOKEN)

@pytest.fixture
def project_id():
    return "3172006893461634976"
```

---

## 5. Business Logic & Algorithms

### 5.1 Mock Pattern for `DoorayBase._request`

All `DoorayBase` subclasses (`Dooray`, `DoorayMessenger`, `DoorayProject`) use `requests.request` internally. The mock target is always `requests.request`.

```
Test calls API method
  → API method calls self._request(method, url, **kwargs)
    → _request calls requests.request(method, endpoint+url, **kwargs)  ← MOCKED HERE
      → Mock returns MagicMock(status_code=200, text="", json=lambda: FIXTURE)
    → _request returns mock response
  → API method parses response and returns result
Test asserts on result AND on mock call args
```

### 5.2 Assertion Strategy

Every unit test must verify **two things**:
1. **Output correctness** — The returned object has correct attributes
2. **Request correctness** — The mock was called with the right HTTP method, URL path, and params/body

```python
# Example: verify both output AND request
@patch("requests.request")
def test_get_tag(self, mock_request):
    mock_resp = MagicMock(status_code=200, text="")
    mock_resp.json.return_value = TAG_RESPONSE
    mock_request.return_value = mock_resp

    result = self._dooray.project.get_tag("proj-1", "tag-1")

    # Assert output
    self.assertEqual(result.result.name, "bug")
    self.assertEqual(result.result.color, "ff0000")

    # Assert request
    mock_request.assert_called_once_with(
        "GET",
        "https://api.dooray.com/project/v1/projects/proj-1/tags/tag-1",
        headers=ANY
    )
```

### 5.3 Migration Steps (for SWE)

1. Create `tests/fixtures/__init__.py` and `tests/fixtures/responses.py`
2. Create `tests/unit/__init__.py`
3. Implement unit test files one by one (order: `test_messenger_hook_attachments` → `test_messenger_hook` → `test_post_builder` → `test_template_builder` → `test_dooray_common` → `test_dooray_messenger` → `test_dooray_project`)
4. Create `tests/integration/__init__.py` and `tests/integration/conftest.py`
5. Move and refactor `test_DoorayProject.py` → `tests/integration/test_dooray_project.py`
6. Move `test_MessengerHook.py` → `tests/integration/test_messenger_hook.py`
7. Update `pytest.ini`
8. Delete old test files from `tests/` root
9. Run `python -m pytest tests/unit` to verify all unit tests pass without API token
10. Run `python -m pytest tests/integration -m integration` to verify integration tests still pass

---

## 6. Security & Constraints

- **No real tokens in unit tests.** All unit tests use `token="test-token"`.
- **`tokens.py` must remain git-skip-worktree.** Never commit real API tokens.
- **Python 3.10 compatibility.** No 3.11+ features in test code.
- **No new test dependencies.** Use only `unittest.mock` (stdlib) — no `pytest-mock`, `responses`, or `httpretty`.
