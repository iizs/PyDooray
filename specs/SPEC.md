# [SPEC] PyDooray - Dooray! REST API Python Wrapper

**Status:** Approved
**Author:** Spec Synchronizer (Sherlock)
**Date:** 2026-02-10
**Target Component:** `src/dooray/`

## 1. Overview

PyDooray is a Python wrapper library for the [Dooray! REST API](https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419). It provides Pythonic access to Dooray! services including **Common** (Members, IncomingHooks), **Messenger** (Channels, Direct Messages), and **Project** (Projects, Posts, Templates, Milestones, Tags, Email Addresses, Hooks, Members, MemberGroups, Post Logs).

The library also provides a standalone **MessengerHook** utility for sending messages via Dooray! Messenger incoming webhooks without requiring API authentication.

### Key Design Principles
- All API calls return standardized response objects (`DoorayResponse` / `DoorayListResponse`)
- Authentication via `dooray-api` token header
- Builder pattern for constructing complex write payloads (`PostBuilder`, `TemplateBuilder`, `MessengerHookAttachments`)
- Data model classes parse JSON `dict` responses into Python objects with snake_case attributes

### Package Metadata
- **Name:** PyDooray
- **Version:** 0.2.0
- **Python:** >= 3.6 (project rule: maintain 3.10 compatibility)
- **Dependencies:** `requests >= 2.14.0`
- **License:** MIT
- **Default API Endpoint:** `https://api.dooray.com`

## 2. Data Model (Schema & Types)

> See detailed spec: [spec_data_models.md](./spec_data_models.md)

### Summary of Data Model Classes

| Module | Class | Description |
|---|---|---|
| `DoorayObjects` | `ResponseHeader` | Parsed API response header (isSuccessful, resultCode, resultMessage) |
| `DoorayObjects` | `DoorayResponse` | Standard single-result API response wrapper |
| `DoorayObjects` | `DoorayListResponse` | Paginated list-result API response wrapper |
| `DoorayObjects` | `Relation` | Simple `{id}` reference object |
| `DoorayExceptions` | `DoorayException` | Base exception class |
| `DoorayExceptions` | `BadHttpResponseStatusCode` | Raised on non-200 HTTP status |
| `DoorayExceptions` | `ServerGeneralError` | Raised when response body is `SERVER_GENERAL_ERROR` |
| `Member` | `Member` | Organization member (id, name, userCode, externalEmailAddress) |
| `IncomingHook` | `IncomingHook` | Incoming hook info (id, name, serviceType, url, projects) |
| `Messenger` | `Channel` | Messenger channel with users, status, type |
| `Messenger` | `Users` | Channel participants container |
| `Messenger` | `Participant` | Channel participant (type + member) |
| `Messenger` | `Me` | Current user in channel (extends Participant with role) |
| `Messenger` | `OrganizationMember` | Simple organizationMemberId reference |
| `Project` | `Project` | Project entity (id, code, description, scope, state, type, organization, wiki, drive) |
| `Project` | `DisplayName` | Localized display name (locale, name) |
| `Project` | `Workflow` | Project workflow (id, name, order, class, names) |
| `Project` | `EmailAddress` | Project email address (id, name, emailAddress) |
| `Project` | `Tag` | Project tag (id, name, color) |
| `Project` | `Milestone` | Project milestone (id, name, status, dates) |
| `Project` | `ProjectMember` | Project member (organizationMemberId, role) |
| `Project` | `MemberGroup` | Project member group (id, code, dates, project, members) |
| `Project` | `MemberGroupMember` | Wrapper around Member for member group context |
| `Project` | `BasePost` | Abstract base for posts/templates (users, body, subject, dueDate, priority) |
| `Project` | `WritePost` | Writable post (extends BasePost with parentPostId, version, milestoneId, tagIds) |
| `Project` | `ReadPost` | Read post (extends BasePost with id, project, taskNumber, workflow, milestone, tags) |
| `Project` | `WriteTemplate` | Writable template (extends BasePost with templateName, guide, isDefault, milestoneId, tagIds) |
| `Project` | `ReadTemplate` | Read template (extends BasePost with id, project, templateName, guide, milestone, tags) |
| `Project` | `PostLog` | Post comment/event log |
| `Project` | `PostUser` | Post user reference (type + member or emailUser) |
| `Project` | `PostUsers` | Post users container (from, to, cc) |
| `Project` | `PostBody` | Post body content (mimeType, content) |

## 3. Interface Design (API / Signatures)

> See detailed spec: [spec_api_interfaces.md](./spec_api_interfaces.md)

### Summary of API Categories

| Class | Category | Methods Count |
|---|---|---|
| `Dooray` | Common > Members | 1 (`get_members`) |
| `Dooray` | Common > IncomingHooks | 1 (`get_incoming_hook`) |
| `DoorayMessenger` | Messenger > Channels | 6 (get, create, send, join, leave) |
| `DoorayProject` | Project > Projects | 3 (is_creatable, create, get) + 1 (get_workflows) |
| `DoorayProject` | Project > EmailAddress | 2 (create, get) |
| `DoorayProject` | Project > Tags | 2 (create, get) |
| `DoorayProject` | Project > Milestones | 5 (CRUD + list) |
| `DoorayProject` | Project > Hooks | 1 (create) |
| `DoorayProject` | Project > Members | 2 (add, get) |
| `DoorayProject` | Project > MemberGroups | 2 (get, get list) |
| `DoorayProject` | Project > Templates | 5 (CRUD + list) |
| `DoorayProject` | Project > Posts | 6 (CRUD + workflow + done) |
| `DoorayProject` | Project > Post Logs | 5 (CRUD + list) |

### Standalone Utilities
| Class | Description | Spec |
|---|---|---|
| `MessengerHook` | Webhook message sender (no auth required) | [spec_messenger_hook.md](./spec_messenger_hook.md) |
| `MessengerHookAttachments` | Builder for webhook attachments | [spec_messenger_hook.md](./spec_messenger_hook.md) |
| `PostBuilder` | Builder for post write payloads | [spec_builders.md](./spec_builders.md) |
| `TemplateBuilder` | Builder for template write payloads | [spec_builders.md](./spec_builders.md) |

## 4. Internal Component Design (Class/Module Structure)

### File Layout
```
src/dooray/
├── __init__.py          # Public exports: Dooray, DoorayMessenger, DoorayProject,
│                        #   MessengerHook, MessengerHookAttachments, TemplateBuilder, PostBuilder
├── Dooray.py            # Core API classes: DoorayBase, Dooray, DoorayMessenger, DoorayProject
├── DoorayExceptions.py  # Exception hierarchy
├── DoorayObjects.py     # Common response wrappers (ResponseHeader, DoorayResponse, DoorayListResponse, Relation)
├── IncomingHook.py      # IncomingHook data model
├── Member.py            # Member data model
├── Messenger.py         # Messenger data models (Channel, Users, Participant, Me, OrganizationMember)
├── MessengerHook.py     # Standalone webhook classes (MessengerHook, MessengerHookAttachments)
└── Project.py           # Project data models + builders (Project, Workflow, Tag, Milestone, Post*, Template*, etc.)
```

### Class Hierarchy
```
DoorayBase (Base HTTP client)
├── Dooray (Main entry point)
│   ├── .messenger → DoorayMessenger
│   └── .project → DoorayProject
├── DoorayMessenger (Messenger API methods)
└── DoorayProject (Project API methods)

DoorayException (Base exception)
├── BadHttpResponseStatusCode
└── ServerGeneralError

BasePost (Abstract post base)
├── WritePost → used by PostBuilder
├── ReadPost
├── WriteTemplate → used by TemplateBuilder
└── ReadTemplate
```

### Entry Point Pattern
```python
import dooray

# Method 1: Full API client
d = dooray.Dooray(token="YOUR_API_TOKEN")
d.messenger.send_channel_message(channel_id, "Hello")
d.project.create_post(project_id, post)

# Method 2: Standalone webhook
hook = dooray.MessengerHook(hook_url="YOUR_HOOK_URL")
hook.send("Hello")
```

## 5. Business Logic & Algorithms

### 5.1 HTTP Request Flow (`DoorayBase._request`)
1. Merge default auth headers (`Authorization: dooray-api {token}`, `User-Agent`) with any caller-provided headers
2. Execute HTTP request via `requests.request(method, endpoint + url, **kwargs)`
3. **IF** `resp.status_code != 200` → raise `BadHttpResponseStatusCode(resp)`
4. **IF** `resp.text == 'SERVER_GENERAL_ERROR'` → raise `ServerGeneralError(resp)`
5. Return the raw `requests.Response` object

### 5.2 Response Parsing Pattern
- Single result: `DoorayResponse(resp.json(), ObjectClass)` → parses `data['header']` + `data['result']`
- List result: `DoorayListResponse(resp.json(), ObjectClass, page, size)` → additionally parses `data['totalCount']` and iterates `data['result']` list
- No result body: `DoorayResponse(resp.json())` → parses only header

### 5.3 Parameter Serialization
- All query parameters are constructed as `dict` and passed as `params=` to requests
- List-type parameters (e.g., `external_emails`) are joined with commas
- Body payloads are serialized via `json=` parameter
- Builder classes provide `to_json_dict()` for JSON-serializable output with camelCase keys

### 5.4 Known Issues (from Code TODOs)
- `get_members`: Returns bad request with no parameters; workaround is passing `name=''` or `userCode=''`
- `tag_ids` param in `get_posts`: Incorrectly mapped to `ccMemberIds` key instead of `tagIds` (bug at line 949 of Dooray.py)
- `IncomingHook`: Unknown `channels` property exists in API response but is not documented
- `Channel`: API doc says `role` field exists but it does not appear in response
- `create_channel`: Creating `direct` type channel returns HTTP 500
- `milestone`: `closedAt` not updated when setting status to `closed` via update API
- `get_milestone`: Returns `200 OK` with `SERVER_GENERAL_ERROR` text for invalid milestone_id
- `get_member_groups`: API returns list of lists (suspected API error)
- `add_member`: Response object differs from API documentation

## 6. Security & Constraints

### Authentication
- **Token-based:** All API calls require a Dooray API token passed in the `Authorization: dooray-api {token}` header
- **MessengerHook exception:** Webhook calls use URL-based authentication (no token header required)

### Input Validation
- Constructor parameters validated via `assert` statements (token, endpoint, user_agent)
- Method-level assertions for required string/list parameters (e.g., `create_tag`, `create_milestone`)

### Constraints
- **Python Compatibility:** Must maintain Python 3.10 compatibility (project rule)
- **Pagination defaults:** `page=0`, `size=20` (max typically 100)
- **Body MIME type:** Always `text/x-markdown` for post/template/log bodies (HTML not yet supported)
- **Date formats for milestone:** `YYYY-MM-DD+ZZ` (e.g., `2019-01-01+00:00`)
- **Date formats for post queries:** `today`, `thisweek`, `prev-{N}d`, `next-{N}d`, or ISO 8601 range

## 7. Detailed Spec Files

| File | Description |
|---|---|
| [spec_data_models.md](./spec_data_models.md) | All data model classes with field types and JSON mappings |
| [spec_api_interfaces.md](./spec_api_interfaces.md) | All API method signatures with endpoints and parameters |
| [spec_messenger_hook.md](./spec_messenger_hook.md) | MessengerHook and MessengerHookAttachments classes |
| [spec_builders.md](./spec_builders.md) | PostBuilder and TemplateBuilder classes |
