# [SPEC] PyDooray - Usability Improvement Notes

**Status:** Draft
**Author:** Tech Lead (Tony)
**Date:** 2026-02-21
**Target Component:** `src/dooray/`

## 1. Overview

This document identifies usability gaps in the current PyDooray package from an **end-user (developer) perspective**. The library currently provides a thin wrapper over the Dooray! REST API with builder classes for complex payloads. While functional, several areas need improvement to deliver a Pythonic, ergonomic developer experience.

### Scope

- Items marked **[API Limitation]** cannot be resolved without upstream Dooray API changes.
- Items marked **[Library Enhancement]** can be implemented within PyDooray.
- Items marked **[Spec Correction]** indicate stale or incorrect spec content that needs updating.

---

## 2. Spec Corrections (Housekeeping)

### 2.1 `get_posts()` tag_ids Bug — Already Fixed [Spec Correction]

**File:** `specs/spec_api_interfaces.md` line 504, `specs/SPEC.md` line 172

The spec still states `tag_ids` is mapped to `ccMemberIds` (P0 bug). However, the current code (`Dooray.py:954-955`) correctly maps it to `tagIds`. The spec must be updated to remove the stale bug annotation.

### 2.2 Package Version Mismatch [Spec Correction]

**File:** `specs/SPEC.md` line 23

The spec states version `0.2.0`, but `setup.cfg` declares version `0.3.0`. The spec must reflect the current version.

### 2.3 Python Version Requirement [Spec Correction]

**File:** `specs/SPEC.md` line 23

The spec states `>= 3.6`, but the project rule and `setup.cfg` require `>= 3.10`. Must be aligned.

---

## 3. Error Handling & Resilience [Library Enhancement]

### 3.1 Overly Generic Exception Types

**Current state:** Only two exception classes exist — `BadHttpResponseStatusCode` and `ServerGeneralError`. Both carry minimal context (just the raw `requests.Response` object).

**Problem:** Callers cannot distinguish between a 400 (bad request), 403 (permission denied), 404 (not found), or 429 (rate limit) without manually inspecting the response object. This forces every caller to write the same boilerplate.

**Proposed improvement:**
- Add semantic exception subclasses: `NotFoundError(404)`, `PermissionDeniedError(403)`, `ValidationError(400)`, `RateLimitError(429)`
- Parse and include Dooray's error response body (`resultCode`, `resultMessage`) in the exception message
- Keep `BadHttpResponseStatusCode` as the catch-all fallback for unrecognized status codes

### 3.2 `assert` Used for Input Validation

**Current state:** Constructor and method parameters are validated with `assert` statements (e.g., `assert token is not None and isinstance(token, str)`).

**Problem:** `assert` is stripped when Python runs with `-O` (optimize) flag, silently disabling all validation. This is a well-known anti-pattern for production code.

**Proposed improvement:**
- Replace all `assert` statements with explicit `if ... raise TypeError/ValueError` checks
- Provide clear error messages (e.g., `"token must be a non-empty string, got: {type(token).__name__}"`)

---

## 4. Pagination UX [Library Enhancement]

### 4.1 No Auto-Pagination Support

**Current state:** All list endpoints (`get_posts`, `get_milestones`, `get_templates`, `get_post_logs`, `get_member_groups`) return a single page. Users must manually loop, check `total_count`, and increment `page`.

**Problem:** Common use case of "get all posts matching criteria" requires boilerplate like:

```python
all_posts = []
page = 0
while True:
    resp = d.project.get_posts(project_id, page=page, size=100)
    all_posts.extend(resp.result)
    if len(all_posts) >= resp.total_count:
        break
    page += 1
```

**Proposed improvement:**
Add an iterator/generator method (e.g., `iter_posts()`) that yields items across pages automatically:

```python
for post in d.project.iter_posts(project_id, post_workflow_classes='registered'):
    print(post.subject)
```

This should be implemented as a generic pagination helper that any list endpoint can use, keeping `get_*` methods for single-page access when explicit control is needed.

---

## 5. Missing List/Search Endpoints [API Limitation]

### 5.1 No Tag Listing

**Current state:** Can `create_tag()` and `get_tag(tag_id)`, but cannot list all tags in a project.

**Impact:** Users must know tag IDs in advance. No way to discover available tags programmatically. This is a significant gap for automation scripts that need to assign tags by name.

**Workaround until API is available:** None. Users must maintain external tag ID mappings.

### 5.2 No Project Listing

**Current state:** Can `get(project_id)` but cannot list all projects the user has access to.

**Impact:** Users must know project IDs in advance. No way to discover projects programmatically.

### 5.3 No Hook Listing

**Current state:** Can `create_hook()` but cannot list or get existing hooks in a project.

**Impact:** Cannot audit or manage existing hooks. Test cleanup is impossible.

### 5.4 No Email Address Listing

**Current state:** Can `create_email_address()` and `get_email_address(id)`, but cannot list all email addresses in a project.

### 5.5 No Member Listing for Projects

**Current state:** Can `add_member()` and `get_member(member_id)`, but cannot list all members of a project.

**Impact:** Common use case of "who is in this project?" requires knowing member IDs in advance.

---

## 6. Builder Pattern Improvements [Library Enhancement]

### 6.1 No Validation Until API Call

**Current state:** Builders accept any value without validation. Missing required fields (e.g., `PostBuilder` without `set_subject()`) only fail at API call time with an opaque server error.

**Proposed improvement:**
- Add a `validate()` method (called automatically by `create()`) that checks required fields
- Raise `ValueError` with clear messages like `"PostBuilder requires set_subject() before create()"`

### 6.2 No `from_read_post()` Factory for Updates

**Current state:** To update a post, users must manually rebuild the entire post from scratch using `PostBuilder`, even if only changing one field.

**Proposed improvement:**
Add a factory method `PostBuilder.from_read_post(read_post)` that pre-populates the builder from an existing `ReadPost` object, allowing partial updates:

```python
existing = d.project.get_post(project_id, post_id).result
updated = dooray.PostBuilder.from_read_post(existing)\
    .set_priority('high')\
    .create()
d.project.update_post(project_id, post_id, updated)
```

### 6.3 Builder Reusability — ✅ Resolved

> **Resolved in:** `99cb954 feat: return deep copy from builder create() for reusability`

All builder classes (`PostBuilder`, `TemplateBuilder`, `MessengerHookAttachments`) now return `copy.deepcopy()` from `create()`, allowing builder reuse as a template for creating multiple similar objects.

---

## 7. Type Safety & IDE Experience [Library Enhancement]

### 7.1 No Type Annotations on Public API

**Current state:** Function signatures lack type hints. For example:

```python
def get_posts(self, project_id,
              page=0, size=20,
              from_email_address=None, ...):
```

**Problem:** IDE autocompletion shows `(self, project_id, page, size, ...)` without types. Users must read docstrings to know parameter types.

**Proposed improvement:**
Add type annotations to all public method signatures and constructors. Must use `from __future__ import annotations` or `typing` module for Python 3.10 compatibility.

### 7.2 Inconsistent Attribute Naming

**Current state:**
- `PostLog.mailUsers` uses camelCase (should be `mail_users`)
- `OrganizationMember.organizationMemberId` uses camelCase (should be `organization_member_id`)

**Proposed improvement:**
Normalize all public attributes to snake_case. This is a breaking change — should be planned for a major version bump or released with deprecation warnings.

---

## 8. Convenience Methods [Library Enhancement]

### 8.1 No `datetime` Support for Date Parameters

**Current state:** All date parameters accept only raw strings:
- Milestone: `'2019-01-01+00:00'`
- Post queries: `'2019-01-01T00:00:00Z~2019-01-02T00:00:00Z'`
- Post due date: ISO 8601 string

**Problem:** Users must manually format `datetime` objects. The milestone date format (`YYYY-MM-DD+ZZ`) is non-standard and easy to get wrong.

**Proposed improvement:**
- Accept both `str` and `datetime` objects in all date parameters
- Auto-format `datetime` → string with correct format per context
- Provide helper constants or methods for common date ranges (`today`, `this_week`, `last_n_days(7)`)

### 8.2 No `find_member_by_name()` Shorthand

**Current state:** To find a member by name, users must call `get_members(name='John')` and iterate `result`.

**Proposed improvement:**
Add convenience method `find_member(name=..., user_code=...) -> Member` that returns the first match or raises `NotFoundError`. This covers the most common use case without pagination boilerplate.

### 8.3 No `get_workflow_by_name()` Shorthand

**Current state:** To set a post's workflow by name (e.g., "In Progress"), users must first fetch all workflows, iterate to find the matching one, then use the ID.

**Proposed improvement:**
Add `get_workflow_by_name(project_id, name) -> Workflow` that encapsulates the lookup.

---

## 9. Response Object Ergonomics [Library Enhancement]

### 9.1 Accessing Results Requires `.result`

**Current state:** Every API call returns `DoorayResponse` or `DoorayListResponse`, requiring `.result` to access the actual data:

```python
project = d.project.get(project_id).result  # Must always add .result
posts = d.project.get_posts(project_id).result  # Same pattern
```

**Problem:** The `.header` metadata is rarely needed by callers. The extra `.result` adds noise to every call.

**Proposed improvement (non-breaking):**
- Keep existing behavior intact
- Add `__iter__` to `DoorayListResponse` so it's directly iterable: `for post in d.project.get_posts(...)`
- Add `__getattr__` proxy or `data` property on `DoorayResponse` for direct attribute access

### 9.2 `DoorayListResponse` Is Not `Sized`

**Current state:** Cannot use `len()` on list responses. Must access `resp.total_count` explicitly.

**Proposed improvement:**
Implement `__len__` returning `len(self.result)` (current page count) and keep `total_count` for the server-side total.

---

## 10. Data Model Convenience [Library Enhancement]

### 10.1 No `__eq__` on Data Models

**Current state:** Model objects use default identity-based equality. Two `Member` objects with the same `id` are not considered equal.

**Problem:** Makes testing and comparisons verbose — users must compare `.id` manually.

**Proposed improvement:**
Implement `__eq__` based on `id` field for all models that have one.

### 10.2 No Dictionary Conversion on Read Models

**Current state:** `to_json_dict()` exists only on Write models. Read models (`ReadPost`, `ReadTemplate`, `Milestone`, etc.) have no serialization method.

**Problem:** Users cannot easily serialize API results for logging, caching, or forwarding.

**Proposed improvement:**
Add `to_dict()` method on all read models, returning a plain `dict` with snake_case keys.

---

## 11. Summary & Priority Matrix

| # | Category | Item | Type | Priority | Breaking? |
|---|---|---|---|---|---|
| 2.1 | Spec | `tag_ids` bug annotation stale | Spec Correction | P0 | No |
| 2.2 | Spec | Version mismatch (0.2.0 vs 0.3.0) | Spec Correction | P0 | No |
| 2.3 | Spec | Python version mismatch (3.6 vs 3.10) | Spec Correction | P0 | No |
| 3.1 | Error | Semantic exception subclasses | Library Enhancement | P1 | No (additive) |
| 3.2 | Error | Replace `assert` with explicit validation | Library Enhancement | P1 | No |
| 4.1 | Pagination | Auto-pagination iterator | Library Enhancement | P1 | No (additive) |
| 6.1 | Builder | Validation on `create()` | Library Enhancement | P2 | No |
| 6.2 | Builder | `from_read_post()` factory | Library Enhancement | P2 | No (additive) |
| 6.3 | Builder | ~~Builder copy on `create()`~~ | ✅ Resolved | — | — |
| 7.1 | Types | Type annotations on public API | Library Enhancement | P2 | No |
| 7.2 | Types | snake_case attribute normalization | Library Enhancement | P3 | Yes |
| 8.1 | Convenience | `datetime` parameter support | Library Enhancement | P2 | No |
| 8.2 | Convenience | `find_member()` shorthand | Library Enhancement | P3 | No (additive) |
| 8.3 | Convenience | `get_workflow_by_name()` | Library Enhancement | P3 | No (additive) |
| 9.1 | Response | Iterable `DoorayListResponse` | Library Enhancement | P2 | No |
| 9.2 | Response | `__len__` on list response | Library Enhancement | P3 | No |
| 10.1 | Model | `__eq__` on data models | Library Enhancement | P3 | No |
| 10.2 | Model | `to_dict()` on read models | Library Enhancement | P3 | No (additive) |
| 5.x | API | Missing list/search endpoints | API Limitation | — | N/A |
