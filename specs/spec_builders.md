# [SPEC] PyDooray - PostBuilder & TemplateBuilder

**Status:** Approved
**Author:** Spec Synchronizer (Sherlock)
**Date:** 2026-02-10
**Target Component:** `src/dooray/Project.py`

## 1. Overview

This document defines the builder classes used to construct write payloads for posts and templates. Both builders follow the fluent builder pattern — each setter method returns `self` for method chaining, and `create()` returns the final writable object.

---

## 2. Class: `PostBuilder`

**File:** `src/dooray/Project.py` (line 265)

### 2.1 Purpose

Constructs a `WritePost` object for use with `DoorayProject.create_post()` and `DoorayProject.update_post()`.

### 2.2 Constructor

```python
PostBuilder()
```

**Internal state:**
- `self._post: WritePost` — Empty `WritePost()` instance (no attributes initialized)

### 2.3 Methods

#### `create() -> WritePost`

Returns the internal `WritePost` object. This is the final step of the builder chain.

#### `set_subject(subject: str) -> PostBuilder`

Sets the post subject.

#### `set_body(body: str) -> PostBuilder`

Sets the post body. Internally creates a `PostBody` with `mimeType='text/x-markdown'` and `content=body`.

#### `set_due_date(due_date: str) -> PostBuilder`

Sets the due date (ISO 8601 format).

#### `set_milestone_id(milestone_id: str) -> PostBuilder`

Sets the associated milestone ID.

#### `set_priority(priority: str) -> PostBuilder`

Sets the priority. Valid values: `'highest'`, `'high'`, `'normal'`, `'low'`, `'lowest'`, `'none'`.

#### `set_version(version: str) -> PostBuilder`

Sets the post version.

#### `set_parent_post_id(parent_post_id: str) -> PostBuilder`

Sets the parent post ID (for sub-tasks).

#### `add_tag_id(tag_id: str) -> PostBuilder`

Adds a tag ID to the post. Initializes `tag_ids` list on first call if not yet set.

#### `add_to_member(member_id: str) -> PostBuilder`

Adds a recipient by member ID. Initializes `PostUsers` on first call if not yet set. Creates a `PostUser` with `type='member'` and `member.organizationMemberId=member_id`.

#### `add_to_email_user(email: str, name: str) -> PostBuilder`

Adds a recipient by email. Creates a `PostUser` with `type='emailUser'` and `emailUser={emailAddress, name}`.

#### `add_cc_member(member_id: str) -> PostBuilder`

Adds a CC recipient by member ID. Same pattern as `add_to_member` but appends to `cc` list.

#### `add_cc_email_user(email: str, name: str) -> PostBuilder`

Adds a CC recipient by email. Same pattern as `add_to_email_user` but appends to `cc` list.

### 2.4 Usage Example

```python
import dooray

d = dooray.Dooray(API_TOKEN)
post = dooray.PostBuilder()\
    .set_subject('test')\
    .set_body('test')\
    .add_to_member(member_id)\
    .create()
d.project.create_post(PROJECT_ID, post)
```

---

## 3. Class: `TemplateBuilder`

**File:** `src/dooray/Project.py` (line 545)

### 3.1 Purpose

Constructs a `WriteTemplate` object for use with `DoorayProject.create_template()` and `DoorayProject.update_template()`.

### 3.2 Constructor

```python
TemplateBuilder()
```

**Internal state:**
- `self._template: WriteTemplate` — Empty `WriteTemplate()` instance (no attributes initialized)

### 3.3 Methods

#### `create() -> WriteTemplate`

Returns the internal `WriteTemplate` object. This is the final step of the builder chain.

#### `set_template_name(template_name: str) -> TemplateBuilder`

Sets the template display name. **Required** — `WriteTemplate.to_json_dict()` always includes `templateName`.

#### `set_subject(subject: str) -> TemplateBuilder`

Sets the template subject.

#### `set_body(body: str) -> TemplateBuilder`

Sets the template body. Internally creates a `PostBody` with `mimeType='text/x-markdown'` and `content=body`.

#### `set_guide(guide: str) -> TemplateBuilder`

Sets the template guide. Internally creates a `PostBody` with `mimeType='text/x-markdown'` and `content=guide`.

#### `set_due_date(due_date: str) -> TemplateBuilder`

Sets the due date (ISO 8601 format).

#### `set_milestone_id(milestone_id: int) -> TemplateBuilder`

Sets the associated milestone ID.

**Note:** The docstring annotates the parameter type as `int`, though in practice milestone IDs are strings in the Dooray API.

#### `set_priority(priority: str) -> TemplateBuilder`

Sets the priority. Valid values: `'highest'`, `'high'`, `'normal'`, `'low'`, `'lowest'`, `'none'`.

#### `set_is_default(is_default: bool) -> TemplateBuilder`

Sets whether this template is the project's default template.

#### `add_tag_id(tag_id: str) -> TemplateBuilder`

Adds a tag ID to the template. Initializes `tag_ids` list on first call if not yet set.

#### `add_to_member(member_id: str) -> TemplateBuilder`

Adds a recipient by member ID. Initializes `PostUsers` on first call if not yet set. Creates a `PostUser` with `type='member'` and `member.organizationMemberId=member_id`.

#### `add_to_email_user(email: str, name: str) -> TemplateBuilder`

Adds a recipient by email. Creates a `PostUser` with `type='emailUser'` and `emailUser={emailAddress, name}`.

#### `add_cc_member(member_id: str) -> TemplateBuilder`

Adds a CC recipient by member ID. Same pattern as `add_to_member` but appends to `cc` list.

#### `add_cc_email_user(email: str, name: str) -> TemplateBuilder`

Adds a CC recipient by email. Same pattern as `add_to_email_user` but appends to `cc` list.

### 3.4 Usage Example

```python
import dooray

d = dooray.Dooray(API_TOKEN)
template = dooray.TemplateBuilder()\
    .set_template_name('Bug Report')\
    .set_subject('Bug: ')\
    .set_body('## Steps to Reproduce\n\n## Expected Behavior\n\n## Actual Behavior')\
    .set_guide('Please fill in the template above.')\
    .add_to_member(member_id)\
    .create()
d.project.create_template(PROJECT_ID, template)
```

---

## 4. Builder → WriteObject → JSON Flow

Both builders follow the same pattern:

```
Builder (fluent API) → WriteObject (data container) → to_json_dict() (JSON-serializable dict)
```

1. Builder methods set attributes on the internal WriteObject
2. `create()` returns the WriteObject
3. API methods call `write_object.to_json_dict()` to serialize for the HTTP request body
4. Only non-None attributes with `hasattr` checks are included in the JSON output
