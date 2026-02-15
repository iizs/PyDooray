# [SPEC] PyDooray - API Interfaces

**Status:** Approved
**Author:** Spec Synchronizer (Sherlock)
**Date:** 2026-02-10
**Target Component:** `src/dooray/Dooray.py`

## 1. Overview

This document defines all API method signatures in the PyDooray library. All API methods are implemented in `Dooray.py` across three classes: `Dooray`, `DoorayMessenger`, and `DoorayProject`, all inheriting from `DoorayBase`.

### API Base Configuration
- **Default Endpoint:** `https://api.dooray.com`
- **Authentication Header:** `Authorization: dooray-api {token}`
- **User-Agent Header:** `User-Agent: PyDooray/Python` (configurable)

---

## 2. Base Class: `DoorayBase`

**File:** `src/dooray/Dooray.py` (line 13)

### 2.1 Constructor

```python
DoorayBase(
    token: str,                           # Required. Dooray API token.
    endpoint: str = "https://api.dooray.com",  # API base URL.
    user_agent: str = "PyDooray/Python"   # User-Agent header value.
)
```

**Assertions:**
- `token` must be a non-None `str`
- `endpoint` must be a non-None `str`
- `user_agent` must be `None` or `str`

**Internal state:**
- `self._token: str`
- `self._endpoint: str`
- `self._request_header: dict` — `{'Authorization': 'dooray-api {token}', 'User-Agent': user_agent}`

### 2.2 `_request(method, url, **kwargs)` (Protected)

Internal HTTP request executor.

**Parameters:**
- `method: str` — HTTP method (`GET`, `POST`, `PUT`, `DELETE`)
- `url: str` — API path (appended to `self._endpoint`)
- `**kwargs` — Passed directly to `requests.request()` (commonly: `params`, `json`, `headers`)

**Logic:**
1. Merge `self._request_header` into `kwargs['headers']` (update existing or set new)
2. Call `requests.request(method, f'{self._endpoint}{url}', **kwargs)`
3. If `resp.status_code != 200` → raise `BadHttpResponseStatusCode(resp)`
4. If `resp.text == 'SERVER_GENERAL_ERROR'` → raise `ServerGeneralError(resp)`
5. Return `resp: requests.Response`

---

## 3. Class: `Dooray` (Main Entry Point)

**Inherits:** `DoorayBase`
**File:** `src/dooray/Dooray.py` (line 51)

### 3.1 Constructor

```python
Dooray(
    token: str,
    endpoint: str = "https://api.dooray.com",
    user_agent: str = "PyDooray/Python"
)
```

**Initializes sub-clients:**
- `self.messenger: DoorayMessenger` — Same token, endpoint, user_agent
- `self.project: DoorayProject` — Same token, endpoint, user_agent

### 3.2 `get_members(...)` — Common > Members

* **Endpoint:** `GET /common/v1/members`
* **Parameters:**

| Parameter | Type | Query Key | Default | Description |
|---|---|---|---|---|
| `name` | `str` | `name` | `None` | Member name filter |
| `user_code` | `str` | `userCode` | `None` | User ID, partial match |
| `user_code_exact` | `str` | `userCodeExact` | `None` | User ID, exact match |
| `id_provider_user_id` | `str` | `idProviderUserId` | `None` | SSO provider user ID |
| `external_emails` | `str` or `list` | `externalEmailAddresses` | `None` | External emails. If `list`, joined with commas. |
| `page` | `int` | `page` | `0` | Page number (starts from 0) |
| `size` | `int` | `size` | `20` | Page size (max 100) |

* **Returns:** `DoorayListResponse` of `Member`
* **Known issue:** Dooray API returns bad request when no query parameter is given.
* **Workaround (REQUIRED):** If no filter parameters (`name`, `user_code`, `user_code_exact`, `id_provider_user_id`, `external_emails`) are provided, the library must automatically inject `name=''` as a default query parameter so that `get_members()` works without requiring the caller to pass an explicit workaround.

### 3.3 `get_incoming_hook(incoming_hook_id)` — Common > IncomingHooks

* **Endpoint:** `GET /common/v1/incoming-hooks/{incoming_hook_id}`
* **Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `incoming_hook_id` | `str` | Incoming hook ID |

* **Returns:** `DoorayResponse` of `IncomingHook`

---

## 4. Class: `DoorayMessenger`

**Inherits:** `DoorayBase`
**File:** `src/dooray/Dooray.py` (line 157)
**Accessed via:** `dooray.Dooray(...).messenger`

### 4.1 Static Helper: `_get_member_id_list(member_ids)`

Normalizes member IDs to a list.
- If `str` → returns `[member_ids]`
- If `list` → returns the list
- Otherwise → assertion error

### 4.2 `get_channels()` — Messenger > Channels

* **Endpoint:** `GET /messenger/v1/channels`
* **Parameters:** None
* **Returns:** `DoorayListResponse` of `Channel` (with `size=None`, meaning unpaginated)

### 4.3 `send_direct_message(member_id, text)` — Messenger > Direct Message

* **Endpoint:** `POST /messenger/v1/channels/direct-send`
* **Request Body:**
```json
{
  "text": "<text>",
  "organizationMemberId": "<member_id>"
}
```
* **Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `member_id` | `str` | Recipient member ID |
| `text` | `str` | Message text |

* **Returns:** `DoorayResponse` (no result object)

### 4.4 `send_channel_message(channel_id, text)` — Messenger > Channel Message

* **Endpoint:** `POST /messenger/v1/channels/{channel_id}/logs`
* **Request Body:**
```json
{
  "text": "<text>"
}
```
* **Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `channel_id` | `str` | Channel ID |
| `text` | `str` | Message text |

* **Returns:** `DoorayResponse` (no result object)

### 4.5 `send_channel_log(channel_id, text)` — Alias

* **Alias for:** `send_channel_message(channel_id, text)`

### 4.6 `join_channel(channel_id, member_ids)` — Messenger > Join Channel

* **Endpoint:** `POST /messenger/v1/channels/{channel_id}/members/join`
* **Request Body:**
```json
{
  "memberIds": ["<member_id_1>", "<member_id_2>"]
}
```
* **Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `channel_id` | `str` | Channel ID |
| `member_ids` | `str` or `list` | Member IDs to add (normalized via `_get_member_id_list`) |

* **Returns:** `DoorayResponse` (no result object)

### 4.7 `leave_channel(channel_id, member_ids)` — Messenger > Leave Channel

* **Endpoint:** `POST /messenger/v1/channels/{channel_id}/members/leave`
* **Request Body:**
```json
{
  "memberIds": ["<member_id_1>", "<member_id_2>"]
}
```
* **Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `channel_id` | `str` | Channel ID |
| `member_ids` | `str` or `list` | Member IDs to remove |

* **Returns:** `DoorayResponse` (no result object)

### 4.8 `create_channel(title, member_ids, ...)` — Messenger > Create Channel

* **Endpoint:** `POST /messenger/v1/channels`
* **Query Parameters:**

| Parameter | Type | Query Key | Default | Description |
|---|---|---|---|---|
| `id_type` | `str` | `idType` | `'memberId'` | ID type: `memberId` or `email` |

* **Request Body:**
```json
{
  "memberIds": ["<member_id_1>"],
  "capacity": 100,
  "type": "private",
  "title": "<title>"
}
```
* **Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | — | Channel title |
| `member_ids` | `list` | — | Member IDs |
| `id_type` | `str` | `'memberId'` | `memberId` or `email` |
| `channel_type` | `str` | `'private'` | `private` or `public` |
| `capacity` | `int` | `100` | Channel capacity |

* **Returns:** `DoorayResponse` of `Relation` (containing created channel ID)
* **Known issues:**
  - Creating `private` channel with same name + members does not return `CHANNEL_ALREADY_EXISTS_ERROR`
  - Creating `direct` channel returns HTTP 500

---

## 5. Class: `DoorayProject`

**Inherits:** `DoorayBase`
**File:** `src/dooray/Dooray.py` (line 317)
**Accessed via:** `dooray.Dooray(...).project`

### 5.1 Project > Projects

#### `is_creatable(code)` — Check Project Creatability

* **Endpoint:** `POST /project/v1/projects/is-creatable`
* **Request Body:** `{"code": "<code>"}`
* **Returns:** `bool` — `True` if creatable, `False` otherwise
* **Logic:** Catches `BadHttpResponseStatusCode` → returns `False`. Otherwise `True`.

#### `create(code, description, scope='private')` — Create Project

* **Endpoint:** `POST /project/v1/projects`
* **Request Body:**
```json
{
  "code": "<code>",
  "description": "<description>",
  "scope": "<scope>"
}
```
* **Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | — | Project name |
| `description` | `str` | — | Project description |
| `scope` | `str` | `'private'` | `private` or `public` |

* **Returns:** `DoorayResponse` of `Relation`

#### `get(project_id)` — Get Project

* **Endpoint:** `GET /project/v1/projects/{project_id}`
* **Returns:** `DoorayResponse` of `Project`

#### `get_workflows(project_id)` — Get Project Workflows

* **Endpoint:** `GET /project/v1/projects/{project_id}/workflows`
* **Returns:** `DoorayListResponse` of `Workflow` (no pagination params passed)

### 5.2 Project > EmailAddress

#### `create_email_address(project_id, email_address, name)` — Create Email Address

* **Endpoint:** `POST /project/v1/projects/{project_id}/email-addresses`
* **Request Body:**
```json
{
  "emailAddress": "<email_address>",
  "name": "<name>"
}
```
* **Returns:** `DoorayResponse` of `Relation`

#### `get_email_address(project_id, email_address_id)` — Get Email Address

* **Endpoint:** `GET /project/v1/projects/{project_id}/email-addresses/{email_address_id}`
* **Returns:** `DoorayResponse` of `EmailAddress`

### 5.3 Project > Tags

#### `create_tag(project_id, name, color)` — Create Tag

* **Endpoint:** `POST /project/v1/projects/{project_id}/tags`
* **Request Body:**
```json
{
  "name": "<name>",
  "color": "<color>"
}
```
* **Assertions:** Both `name` and `color` must be non-None strings.
* **Color format:** 6-digit hexadecimal without `#` prefix (e.g., `ff0000`)
* **Returns:** `DoorayResponse` of `Relation`

#### `get_tag(project_id, tag_id)` — Get Tag

* **Endpoint:** `GET /project/v1/projects/{project_id}/tags/{tag_id}`
* **Returns:** `DoorayResponse` of `Tag`

### 5.4 Project > Milestones

#### `create_milestone(project_id, name, start_at, end_at)` — Create Milestone

* **Endpoint:** `POST /project/v1/projects/{project_id}/milestones`
* **Request Body:**
```json
{
  "name": "<name>",
  "startedAt": "<start_at>",
  "endedAt": "<end_at>"
}
```
* **Assertions:**
  - `name`: non-None `str`
  - `start_at`: non-None `str` or `datetime`
  - `end_at`: non-None `str` or `datetime`
* **Date format:** `YYYY-MM-DD+ZZ` (e.g., `2019-01-01+00:00`)
* **Returns:** `DoorayResponse` of `Relation`
* **Known issues:**
  - Date displayed as previous day in KST timezone
  - Dates always converted to KST internally

#### `get_milestones(project_id, page=0, size=20, status=None)` — List Milestones

* **Endpoint:** `GET /project/v1/projects/{project_id}/milestones`
* **Query Parameters:**

| Parameter | Type | Query Key | Default | Description |
|---|---|---|---|---|
| `page` | `int` | `page` | `0` | Page number |
| `size` | `int` | `size` | `20` | Page size |
| `status` | `str` | `status` | `None` | `open` or `closed` filter |

* **Returns:** `DoorayListResponse` of `Milestone`

#### `get_milestone(project_id, milestone_id)` — Get Milestone

* **Endpoint:** `GET /project/v1/projects/{project_id}/milestones/{milestone_id}`
* **Returns:** `DoorayResponse` of `Milestone`
* **Known issue:** Invalid milestone_id returns HTTP 200 with `SERVER_GENERAL_ERROR` text body.

#### `update_milestone(project_id, milestone_id, name, status, start_at, end_at)` — Update Milestone

* **Endpoint:** `PUT /project/v1/projects/{project_id}/milestones/{milestone_id}`
* **Request Body:**
```json
{
  "name": "<name>",
  "status": "<status>",
  "startedAt": "<start_at>",
  "endedAt": "<end_at>"
}
```
* **Assertions:** `name` and `status` must be non-None strings.
* **Returns:** `DoorayResponse` (no result object)
* **Known issue:** `closedAt` field is not updated when setting status to `closed`.

#### `delete_milestone(project_id, milestone_id)` — Delete Milestone

* **Endpoint:** `DELETE /project/v1/projects/{project_id}/milestones/{milestone_id}`
* **Returns:** `DoorayResponse` (no result object)

### 5.5 Project > Hooks

#### `create_hook(project_id, url, send_events)` — Create Project Hook

* **Endpoint:** `POST /project/v1/projects/{project_id}/hooks`
* **Request Body:**
```json
{
  "url": "<url>",
  "sendEvents": ["postCreated", "postCommentCreated"]
}
```
* **Assertions:** `url` must be non-None `str`, `send_events` must be non-None `list`.
* **Valid events:** `postCreated`, `postCommentCreated`, `postTagChanged`, `postDueDateChanged`, `postWorkflowChanged`
* **Returns:** `DoorayResponse` of `Relation`

### 5.6 Project > Members

#### `add_member(project_id, member_id, role='member')` — Add Project Member

* **Endpoint:** `POST /project/v1/projects/{project_id}/members`
* **Request Body:**
```json
{
  "organizationMemberId": "<member_id>",
  "role": "<role>"
}
```
* **Assertions:** `member_id` and `role` must be non-None strings.
* **Returns:** `DoorayResponse` of `ProjectMember`
* **Known issues:**
  - Response object differs from API documentation
  - Adding an existing member silently succeeds with same response

#### `get_member(project_id, member_id)` — Get Project Member

* **Endpoint:** `GET /project/v1/projects/{project_id}/members/{member_id}`
* **Returns:** `DoorayResponse` of `ProjectMember`

### 5.7 Project > MemberGroups

#### `get_member_groups(project_id, page=0, size=20)` — List Member Groups

* **Endpoint:** `GET /project/v1/projects/{project_id}/member-groups`
* **Query Parameters:** `page`, `size`
* **Returns:** `DoorayListResponse` of `MemberGroup`
* **Known issue:** API returns list of lists (suspected API error); does not work correctly.

#### `get_member_group(project_id, member_group_id)` — Get Member Group

* **Endpoint:** `GET /project/v1/projects/{project_id}/member-groups/{member_group_id}`
* **Returns:** `DoorayResponse` of `MemberGroup`

### 5.8 Project > Templates

#### `create_template(project_id, template)` — Create Template

* **Endpoint:** `POST /project/v1/projects/{project_id}/templates`
* **Request Body:** `template.to_json_dict()` (from `TemplateBuilder.create()`)
* **Returns:** `DoorayResponse` of `Relation`

#### `get_templates(project_id, page=0, size=20)` — List Templates

* **Endpoint:** `GET /project/v1/projects/{project_id}/templates`
* **Query Parameters:** `page`, `size`
* **Returns:** `DoorayListResponse` of `ReadTemplate`

#### `get_template(project_id, template_id, interpolation=False)` — Get Template

* **Endpoint:** `GET /project/v1/projects/{project_id}/templates/{template_id}`
* **Query Parameters:**

| Parameter | Type | Query Key | Default | Description |
|---|---|---|---|---|
| `interpolation` | `bool` | `interpolation` | `False` | If `True`, returns interpolated template (variables replaced) |

* **Returns:** `DoorayResponse` of `ReadTemplate`

#### `update_template(project_id, template_id, template)` — Update Template

* **Endpoint:** `PUT /project/v1/projects/{project_id}/templates/{template_id}`
* **Request Body:** `template.to_json_dict()`
* **Returns:** `DoorayResponse` (no result object)

#### `delete_template(project_id, template_id)` — Delete Template

* **Endpoint:** `DELETE /project/v1/projects/{project_id}/templates/{template_id}`
* **Returns:** `DoorayResponse` (no result object)

### 5.9 Project > Posts

#### `create_post(project_id, post)` — Create Post

* **Endpoint:** `POST /project/v1/projects/{project_id}/posts`
* **Request Body:** `post.to_json_dict()` (from `PostBuilder.create()`)
* **Returns:** `DoorayResponse` of `Relation`
* **Known issues:** `parentPostId` seems not working correctly; HTML body not supported.

#### `get_posts(project_id, ...)` — List Posts

* **Endpoint:** `GET /project/v1/projects/{project_id}/posts`
* **Query Parameters:**

| Parameter | Type | Query Key | Default | Description |
|---|---|---|---|---|
| `page` | `int` | `page` | `0` | Page number |
| `size` | `int` | `size` | `20` | Page size |
| `from_email_address` | `str` | `fromEmailAddress` | `None` | Sender email filter |
| `from_member_ids` | `str` | `fromMemberIds` | `None` | Sender member ID filter |
| `to_member_ids` | `str` | `toMemberIds` | `None` | Recipient member ID filter |
| `cc_member_ids` | `str` | `ccMemberIds` | `None` | CC member ID filter |
| `tag_ids` | `str` | **BUG: mapped to `ccMemberIds`** | `None` | Tag ID filter (has a bug - see below) |
| `parent_post_id` | `str` | `parentPostId` | `None` | Parent post filter |
| `post_workflow_classes` | `str` or `list` | `postWorkflowClasses` | `None` | Workflow class filter |
| `post_workflow_ids` | `str` or `list` | `postWorkflowIds` | `None` | Workflow ID filter |
| `milestone_ids` | `str` | `milestoneIds` | `None` | Milestone ID filter |
| `created_at` | `str` | `createdAt` | `None` | Creation date filter |
| `updated_at` | `str` | `updatedAt` | `None` | Update date filter |
| `due_at` | `str` | `dueAt` | `None` | Due date filter |
| `order` | `str` | `order` | `None` | Sort order |

**Date format options for `created_at`, `updated_at`, `due_at`:**
- `today`
- `thisweek` (week starts Monday)
- `prev-{N}d` (e.g., `prev-7d`)
- `next-{N}d` (e.g., `next-7d`)
- `{ISO8601}~{ISO8601}` (e.g., `2019-01-01T00:00:00Z~2019-01-02T00:00:00Z`)

**Order options:** `postDueAt`, `postUpdatedAt`, `createdAt`, `-postDueAt`, `-postUpdatedAt`, `-createdAt` (prefix `-` for descending)

* **Returns:** `DoorayListResponse` of `ReadPost`

**FIX REQUIRED (P0):** `tag_ids` parameter must be mapped to query key `tagIds`.
```python
# Correct implementation:
if tag_ids is not None:
    params['tagIds'] = tag_ids
```

#### `get_post(project_id, post_id)` — Get Post

* **Endpoint:** `GET /project/v1/projects/{project_id}/posts/{post_id}`
* **Returns:** `DoorayResponse` of `ReadPost`

#### `update_post(project_id, post_id, post)` — Update Post

* **Endpoint:** `PUT /project/v1/projects/{project_id}/posts/{post_id}`
* **Request Body:** `post.to_json_dict()`
* **Returns:** `DoorayResponse` (no result object)

#### `set_post_workflow_for_member(project_id, post_id, member_id, workflow_id)` — Set Workflow for Member

* **Endpoint:** `PUT /project/v1/projects/{project_id}/posts/{post_id}/to/{member_id}`
* **Request Body:** `{"workflowId": "<workflow_id>"}`
* **Returns:** `DoorayResponse` (no result object)

#### `set_post_workflow(project_id, post_id, workflow_id)` — Set Post Workflow

* **Endpoint:** `POST /project/v1/projects/{project_id}/posts/{post_id}/set-workflow`
* **Request Body:** `{"workflowId": "<workflow_id>"}`
* **Returns:** `DoorayResponse` (no result object)

#### `set_post_as_done(project_id, post_id)` — Set Post as Done

* **Endpoint:** `POST /project/v1/projects/{project_id}/posts/{post_id}/set-done`
* **Request Body:** None
* **Returns:** `DoorayResponse` (no result object)

### 5.10 Project > Post Logs

#### `create_post_log(project_id, post_id, content)` — Create Post Log

* **Endpoint:** `POST /project/v1/projects/{project_id}/posts/{post_id}/logs`
* **Request Body:**
```json
{
  "body": {
    "content": "<content>",
    "mimeType": "text/x-markdown"
  }
}
```
* **Returns:** `DoorayResponse` of `Relation`

#### `get_post_logs(project_id, post_id, page=None, size=None, order=None)` — List Post Logs

* **Endpoint:** `GET /project/v1/projects/{project_id}/posts/{post_id}/logs`
* **Query Parameters:**

| Parameter | Type | Query Key | Default | Description |
|---|---|---|---|---|
| `page` | `int` | `page` | `None` | Page number |
| `size` | `int` | `size` | `None` | Page size |
| `order` | `str` | `order` | `None` | `createdAt` or `-createdAt` |

* **Returns:** `DoorayListResponse` of `PostLog`

#### `get_post_log(project_id, post_id, log_id)` — Get Post Log

* **Endpoint:** `GET /project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}`
* **Returns:** `DoorayResponse` of `PostLog`

#### `update_post_log(project_id, post_id, log_id, content)` — Update Post Log

* **Endpoint:** `PUT /project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}`
* **Request Body:**
```json
{
  "body": {
    "content": "<content>",
    "mimeType": "text/x-markdown"
  }
}
```
* **Returns:** `DoorayResponse` (no result object)

#### `delete_post_log(project_id, post_id, log_id)` — Delete Post Log

* **Endpoint:** `DELETE /project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}`
* **Returns:** `DoorayResponse` (no result object)

---

## 6. Unavailable APIs (Confirmed against Dooray API docs, 2026-02-14)

The following operations are referenced as TODOs in source code but **do not exist in the Dooray REST API**. These cannot be implemented until Dooray provides the endpoints.

| Category | Operation | Status |
|---|---|---|
| Project > EmailAddress | Delete | Not provided by Dooray API |
| Project > Tags | Delete | Not provided by Dooray API |
| Project > Hooks | Delete | Not provided by Dooray API |
| Project > Posts | Delete | Not provided by Dooray API |
