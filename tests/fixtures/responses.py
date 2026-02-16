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
