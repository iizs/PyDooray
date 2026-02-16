# [SPEC] PyDooray - Data Models

**Status:** Approved
**Author:** Spec Synchronizer (Sherlock)
**Date:** 2026-02-10
**Target Component:** `src/dooray/DoorayObjects.py`, `src/dooray/DoorayExceptions.py`, `src/dooray/Member.py`, `src/dooray/IncomingHook.py`, `src/dooray/Messenger.py`, `src/dooray/Project.py`

## 1. Overview

This document defines every data model class in the PyDooray library. Each class is a plain Python object that accepts a `dict` (parsed from JSON API response) in its constructor and exposes snake_case attributes. Classes that support write operations also provide a `to_json_dict()` method that serializes back to camelCase JSON-compatible `dict`.

---

## 2. Exception Classes

**File:** `src/dooray/DoorayExceptions.py`

### 2.1 `DoorayException`
- **Inherits:** `Exception`
- **Purpose:** Base exception for all PyDooray errors.

### 2.2 `BadHttpResponseStatusCode`
- **Inherits:** `DoorayException`
- **Constructor:** `__init__(self, resp)`
  - `resp`: `requests.Response` object
- **Attributes:**
  - `message: str` — `"Server has returned HTTP Response Status Code {resp.status_code}"`
- **Raised when:** HTTP response status code is not `200`

### 2.3 `ServerGeneralError`
- **Inherits:** `DoorayException`
- **Constructor:** `__init__(self, resp)`
  - `resp`: `requests.Response` object
- **Attributes:**
  - `message: str` — `"Server has returned 'SERVER_GENERAL_ERROR'"`
- **Raised when:** HTTP response body text equals `"SERVER_GENERAL_ERROR"`

---

## 3. Common Response Objects

**File:** `src/dooray/DoorayObjects.py`

### 3.1 `ResponseHeader`

Parses the `header` field from all Dooray API JSON responses.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `is_successful` | `bool` | `isSuccessful` | Whether the request was successful |
| `result_code` | `int` | `resultCode` | Numeric result code |
| `result_message` | `str` | `resultMessage` | Human-readable result message |

**`__repr__`:** Returns formatted string with all attributes.

### 3.2 `DoorayResponse`

Standard wrapper for single-result API responses.

**Constructor:** `__init__(self, data: dict, obj=None)`

| Parameter | Type | Description |
|---|---|---|
| `data` | `dict` | Full JSON response body |
| `obj` | `class` or `None` | Object class to instantiate from `data['result']`. If `None`, `result` attribute is not set. |

| Attribute | Type | Description |
|---|---|---|
| `header` | `ResponseHeader` | Parsed response header |
| `result` | `obj(data['result'])` or absent | Parsed result object (only set when `obj` is not `None`) |

**Logic:**
1. Always parse `data['header']` into `self.header`
2. If `obj is not None`, parse `data['result']` by calling `obj(data['result'])` and assign to `self.result`

### 3.3 `DoorayListResponse`

Paginated list wrapper. **Inherits from `DoorayResponse`**.

**Constructor:** `__init__(self, data: dict, obj: class, page: int = 0, size: int = 20)`

| Parameter | Type | Description |
|---|---|---|
| `data` | `dict` | Full JSON response body |
| `obj` | `class` | Object class to instantiate for each element in `data['result']` |
| `page` | `int` | Current page number (default: `0`) |
| `size` | `int` or `None` | Page size (default: `20`). If `None`, indicates unpaginated response. |

| Attribute | Type | Description |
|---|---|---|
| `header` | `ResponseHeader` | Parsed response header (inherited) |
| `total_count` | `int` | Total number of items (from `data['totalCount']`) |
| `page` | `int` | Current page number |
| `size` | `int` | Page size |
| `result` | `list[obj]` | List of parsed result objects |

**Logic:**
1. Call `super().__init__(data)` — parses header only (no `obj` passed to parent)
2. Set `self.total_count` from `data['totalCount']`
3. Set `self.page` and `self.size` from constructor args
4. Iterate `data['result']`, construct `obj(element)` for each, append to `self.result` list
5. **Special case:** If `self.size is None` → reset `self.page = 0` and `self.size = self.total_count` (indicates all-at-once fetch, used by `get_channels`)

### 3.4 `Relation`

Simple ID-reference object returned as `result` in creation responses.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `id` | `str` | `id` | The resource ID |

---

## 4. Member Model

**File:** `src/dooray/Member.py`

### 4.1 `Member`

Represents an organization member.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Member ID |
| `name` | `str` | `name` | Yes | Display name |
| `user_code` | `str` or `None` | `userCode` | No | User login code |
| `external_email_address` | `str` or `None` | `externalEmailAddress` | No | External email |

**Optional field handling:** Uses `data['key'] if 'key' in data else None` pattern.

---

## 5. IncomingHook Model

**File:** `src/dooray/IncomingHook.py`
**Imports:** `dooray.DoorayObjects`

### 5.1 `IncomingHook`

Represents an incoming webhook configuration.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `id` | `str` | `id` | Hook ID |
| `name` | `str` | `name` | Hook name |
| `service_type` | `str` | `serviceType` | Service type |
| `url` | `str` | `url` | Hook URL |
| `projects` | `list[Relation]` | `projects` | List of associated project references |

**Logic:** Iterates `data['projects']`, creates `Relation(e)` for each, appends to `self.projects`.

**Known issue (TODO):** API response contains an unknown `channels: []` property not yet documented.

---

## 6. Messenger Models

**File:** `src/dooray/Messenger.py`
**Imports:** `dooray.DoorayObjects`

### 6.1 `Channel`

Represents a messenger channel.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Channel ID |
| `title` | `str` | `title` | Yes | Channel title |
| `organization` | `Relation` | `organization` | Yes | Organization reference |
| `type` | `str` | `type` | Yes | Channel type: `direct`, `private`, `me`, `bot` |
| `users` | `Users` | `users` | Yes | Channel participants |
| `me` | `Me` | `me` | Yes | Current user in channel |
| `capacity` | `int` | `capacity` | Yes | Channel member capacity |
| `status` | `str` | `status` | Yes | Status: `system`, `normal`, `archived`, `deleted` |
| `created_at` | `str` | `createdAt` | Yes | ISO timestamp |
| `updated_at` | `str` | `updatedAt` | Yes | ISO timestamp |
| `archived_at` | `str` or `None` | `archivedAt` | Yes | ISO timestamp or null |
| `displayed` | `bool` | `displayed` | Yes | Whether channel is displayed |

**Known issue (TODO):** API documentation mentions a `role` field, but it does not appear in actual responses.

### 6.2 `Users`

Container for channel participants.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `participants` | `list[Participant]` | `participants` | List of participants |

**Logic:** List comprehension `[Participant(e) for e in data['participants']]`

### 6.3 `Participant`

A single channel participant.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `type` | `str` | `type` | Participant type |
| `member` | `OrganizationMember` | `member` | Member reference |

### 6.4 `Me`

Current user's participation. **Inherits from `Participant`**.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `type` | `str` | `type` | Inherited from Participant |
| `member` | `OrganizationMember` | `member` | Inherited from Participant |
| `role` | `str` | `role` | Role in channel: `admin`, `member`, `creator` |

### 6.5 `OrganizationMember`

Simple member reference used within Messenger context.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `organizationMemberId` | `str` | `organizationMemberId` | Organization member ID |

**Note:** This attribute uses camelCase (not snake_case), matching the API field name directly.

---

## 7. Project Models

**File:** `src/dooray/Project.py`
**Imports:** `dooray.DoorayObjects`, `dooray.Member.Member`

### 7.1 `Project`

Represents a Dooray project.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Project ID |
| `code` | `str` | `code` | Yes | Project code/name |
| `description` | `str` or `None` | `description` | No | Project description |
| `scope` | `str` or `None` | `scope` | No | `private` or `public` |
| `state` | `str` or `None` | `state` | No | Project state (undocumented) |
| `type` | `str` or `None` | `type` | No | Project type (undocumented) |
| `organization` | `Relation` or `None` | `organization` | No | Organization reference (undocumented) |
| `wiki` | `Relation` or `None` | `wiki` | No | Wiki reference (undocumented) |
| `drive` | `Relation` or `None` | `drive` | No | Drive reference (undocumented) |

**Optional field handling:** `None if 'key' not in data else data['key']` (or `Relation(data['key'])` for reference types).

**Note:** Fields `state`, `type`, `organization`, `wiki`, `drive` are undocumented in the Dooray API but present in responses.

### 7.2 `DisplayName`

Localized name representation.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `locale` | `str` | `locale` | Locale code (e.g., `ko_KR`, `en_US`) |
| `name` | `str` | `name` | Localized display name |

### 7.3 `Workflow`

Project workflow state definition.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Workflow ID |
| `name` | `str` | `name` | Yes | Workflow name |
| `order` | `int` or `None` | `order` | No | Display order |
| `workflow_class` | `str` or `None` | `class` | No | Workflow classification: `registered`, `working`, `closed` |
| `names` | `list[DisplayName]` | `names` | No | Localized names (empty list if absent) |

**Logic for `names`:** If `'names' in data`, iterate and create `DisplayName(e)` for each. Otherwise, empty list.

### 7.4 `EmailAddress`

Project email address.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` or `None` | `id` | No | Email address ID |
| `name` | `str` | `name` | Yes | Display name |
| `email_address` | `str` | `emailAddress` | Yes | Email address |

**`to_json_dict()` output:**
```json
{
  "name": "<name>",
  "emailAddress": "<email_address>",
  "id": "<id>"  // only if id is not None
}
```

### 7.5 `Tag`

Project tag.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Tag ID |
| `name` | `str` or `None` | `name` | No | Tag name |
| `color` | `str` or `None` | `color` | No | Hexadecimal color (e.g., `00ff00`) |

### 7.6 `Milestone`

Project milestone.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Milestone ID |
| `name` | `str` | `name` | Yes | Milestone name |
| `status` | `str` or `None` | `status` | No | `open` or `closed` |
| `started_at` | `str` or `None` | `startedAt` | No | Start date. Absent for milestones without a period. |
| `ended_at` | `str` or `None` | `endedAt` | No | End date |
| `closed_at` | `str` or `None` | `closedAt` | No | Close timestamp |
| `created_at` | `str` or `None` | `createdAt` | No | Creation timestamp |
| `updated_at` | `str` or `None` | `updatedAt` | No | Last update timestamp |

### 7.7 `ProjectMember`

Member within a project context.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `organization_member_id` | `str` | `organizationMemberId` | Yes | Organization member ID |
| `role` | `str` or `None` | `role` | No | Role in project |

**`to_json_dict()` output:**
```json
{
  "organizationMemberId": "<organization_member_id>",
  "role": "<role>"  // only if role is not None
}
```

### 7.8 `MemberGroup`

Project member group.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Member group ID |
| `code` | `str` | `code` | Yes | Group code |
| `created_at` | `str` | `createdAt` | Yes | Creation timestamp |
| `updated_at` | `str` | `updatedAt` | Yes | Last update timestamp |
| `project` | `Project` | `project` | Yes | Parent project object |
| `members` | `list[MemberGroupMember]` | `members` | No | Member list (only if key exists in data) |

### 7.9 `MemberGroupMember`

Wrapper for a member within a member group.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | Description |
|---|---|---|
| `organization_member` | `Member` | Constructed as `Member(data)` — the entire `data` dict is passed directly |

### 7.10 `PostBody`

Post/template/log body content.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `mime_type` | `str` | `mimeType` | MIME type (always `text/x-markdown` for writes) |
| `content` | `str` | `content` | Text content |

**`to_json_dict()` output:**
```json
{
  "mimeType": "<mime_type>",
  "content": "<content>"
}
```

### 7.11 `PostUser`

A user reference within post context (can be member or email user).

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `type` | `str` | `type` | Yes | `member` or `emailUser` |
| `member` | `ProjectMember` or `None` | `member` | No | Set if type is `member` |
| `email_user` | `EmailAddress` or `None` | `emailUser` | No | Set if type is `emailUser` |

**`to_json_dict()` logic:**
1. Start with `{'type': self.type}`
2. If `self.type == 'member'` → add `'member': self.member.to_json_dict()`
3. If `self.type == 'emailUser'` → add `'emailUser': self.email_user.to_json_dict()`

### 7.12 `PostUsers`

Container for post sender and recipients.

**Constructor:** `__init__(self, data: dict = None)`

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `user_from` | `PostUser` or `None` | `from` | Sender (None if no data or key absent) |
| `to` | `list[PostUser]` | `to` | Recipients list |
| `cc` | `list[PostUser]` | `cc` | CC recipients list |

**Logic:**
- If `data is not None`: parse `from`, `to`, `cc` from data
- If `data is None`: initialize `user_from = None`, `to = []`, `cc = []` (used by builders)

**`to_json_dict()` output:**
```json
{
  "from": null,  // or PostUser serialized
  "to": [ /* PostUser.to_json_dict() for each */ ],
  "cc": [ /* PostUser.to_json_dict() for each */ ]
}
```

### 7.13 `BasePost` (Abstract)

Base class for post and template models.

**Constructor:** `__init__(self, data: dict = None)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `users` | `PostUsers` or `None` | `users` | No | Post users (to/cc) |
| `body` | `PostBody` or `None` | `body` | No | Post body |
| `subject` | `str` | `subject` | Yes (if data) | Post subject line |
| `due_date` | `str` or `None` | `dueDate` | No | Due date |
| `due_date_flag` | `str` or `None` | `dueDateFlag` | No | Due date flag (deprecated per post API doc) |
| `priority` | `str` or `None` | `priority` | No | `highest`, `high`, `normal`, `low`, `lowest`, `none` |

**Logic:** If `data is None`, no attributes are initialized (used by builders which set attributes manually).

### 7.14 `WritePost`

Writable post model. **Inherits from `BasePost`**.

**Constructor:** `__init__(self, data: dict = None)`

Additional attributes (beyond BasePost):

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `parent_post_id` | `str` | `parentPostId` | Parent post ID |
| `version` | `str` or `None` | `version` | Post version |
| `milestone_id` | `str` | `milestoneId` | Associated milestone ID |
| `tag_ids` | `list[str]` | `tagIds` | Associated tag IDs |

**`to_json_dict()` logic:**
Constructs a dict including only attributes that are set (non-None) and `hasattr` check:
- `users` → `self.users.to_json_dict()`
- `body` → `self.body.to_json_dict()`
- `subject` → string
- `dueDate` → string
- `dueDateFlag` → string
- `milestoneId` → string
- `tagIds` → list of strings
- `priority` → string
- `version` → string
- `parentPostId` → string

### 7.15 `ReadPost`

Read-only post model. **Inherits from `BasePost`**.

**Constructor:** `__init__(self, data: dict)`

Additional attributes (beyond BasePost):

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Post ID |
| `project` | `Project` or `None` | `project` | No | Parent project |
| `task_number` | `int` or `None` | `taskNumber` | No | Task sequential number |
| `closed` | `bool` or `None` | `closed` | No | Whether post is closed |
| `closed_at` | `str` or `None` | `closedAt` | No | Close timestamp |
| `updated_at` | `str` or `None` | `updatedAt` | No | Update timestamp |
| `number` | `int` | `number` | Yes | Post number |
| `parent` | `ReadPost` or `None` | `parent` | No | Parent post (recursive) |
| `workflow_class` | `str` or `None` | `workflowClass` | No | `registered`, `working`, `closed` |
| `workflow` | `Workflow` or `None` | `workflow` | No | Current workflow state |
| `milestone` | `Milestone` or `None` | `milestone` | No | Associated milestone. **Special:** Only parsed if key exists AND value is not `None` |
| `tags` | `list[Tag]` | `tags` | No | Associated tags (empty list if absent) |

### 7.16 `WriteTemplate`

Writable template model. **Inherits from `BasePost`**.

**Constructor:** `__init__(self, data: dict = None)`

Additional attributes (beyond BasePost):

| Attribute | Type | JSON Key | Description |
|---|---|---|---|
| `template_name` | `str` | `templateName` | Template display name |
| `guide` | `PostBody` | `guide` | Template guide content |
| `is_default` | `bool` | `isDefault` | Whether this is the default template |
| `milestone_id` | `str` | `milestoneId` | Associated milestone ID |
| `tag_ids` | `list[str]` | `tagIds` | Associated tag IDs |

**`to_json_dict()` logic:**
Essential field: `templateName` is always included. All other fields are included only if set and non-None.
Keys: `users`, `body`, `guide`, `subject`, `dueDate`, `dueDateFlag`, `milestoneId`, `tagIds`, `priority`, `isDefault`.

### 7.17 `ReadTemplate`

Read-only template model. **Inherits from `BasePost`**.

**Constructor:** `__init__(self, data: dict)`

Additional attributes (beyond BasePost):

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Template ID |
| `project` | `Project` | `project` | Yes | Parent project |
| `template_name` | `str` | `templateName` | Yes | Template display name |
| `guide` | `PostBody` or `None` | `guide` | No | Template guide |
| `is_default` | `bool` | `isDefault` | Yes | Whether this is the default template |
| `milestone` | `Milestone` or `None` | `milestone` | No | Associated milestone (absent if not set) |
| `tags` | `list[Tag]` | `tags` | Yes | Associated tags |

### 7.18 `PostLog`

Post comment or event log entry.

**Constructor:** `__init__(self, data: dict)`

| Attribute | Type | JSON Key | Required | Description |
|---|---|---|---|---|
| `id` | `str` | `id` | Yes | Log ID |
| `post` | `Relation` | `post` | Yes | Parent post reference |
| `type` | `str` | `type` | Yes | Log type: `comment` or `event` |
| `subtype` | `str` | `subtype` | Yes | Subtype: `general`, `from_email`, `sent_email` |
| `created_at` | `str` | `createdAt` | Yes | Creation timestamp |
| `modified_at` | `str` or `None` | `modifiedAt` | No | Last modified timestamp |
| `creator` | `PostUser` | `creator` | Yes | Log creator |
| `mailUsers` | `PostUsers` or `None` | `mailUsers` | No | Mail recipients (if email-related) |
| `body` | `PostBody` | `body` | Yes | Log content |

**Note:** `mailUsers` attribute uses camelCase (inconsistent with other attributes).
