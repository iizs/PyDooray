# [SPEC] PyDooray - MessengerHook & MessengerHookAttachments

**Status:** Approved
**Author:** Spec Synchronizer (Sherlock)
**Date:** 2026-02-10
**Target Component:** `src/dooray/MessengerHook.py`

## 1. Overview

This document defines the standalone webhook utility classes that allow sending messages to Dooray! Messenger incoming webhooks **without requiring API authentication**. These classes are independent of the main `DoorayBase` class hierarchy.

---

## 2. Class: `MessengerHook`

**File:** `src/dooray/MessengerHook.py` (line 4)
**Imports:** `requests`

### 2.1 Purpose

Sends messages to a Dooray! Messenger incoming hook URL. Unlike the main API classes, this does not require a Dooray API token — authentication is URL-based.

### 2.2 Constructor

```python
MessengerHook(
    hook_url: str,                          # Required. The incoming hook URL.
    hook_name: str = "My Bot",              # Bot display name.
    hook_icon: str = "https://static.dooray.com/static_images/dooray-bot.png",  # Bot icon URL.
    user_agent: str = "PyDooray/Python"     # User-Agent header value.
)
```

**Assertions:**
- `hook_url` must be a non-None `str`
- `hook_name` must be a non-None `str`
- `hook_icon` must be a non-None `str`
- `user_agent` must be `None` or `str`

**Internal state:**
- `self._hook_url: str`
- `self._hook_name: str`
- `self._hook_icon: str`
- `self._request_header: dict` — `{'User-Agent': user_agent}`

### 2.3 `send(text, attachments=None)` — Send Message

Sends a message to the configured hook URL.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | `str` | — | Message text (required) |
| `attachments` | `list` or `None` | `None` | List of attachment dicts. Use `MessengerHookAttachments` to build. |

**Assertions:**
- `text` must be a non-None `str`
- `attachments` must be `None` or `list`

**Request:**
- **Method:** `POST`
- **URL:** `self._hook_url`
- **Headers:** `self._request_header` (User-Agent only)
- **Body (JSON):**
```json
{
  "botName": "<hook_name>",
  "botIconImage": "<hook_icon>",
  "text": "<text>",
  "attachments": [...]  // only if attachments is not None
}
```

**Returns:** `bool` — `True` if message was sent successfully (`status_code == 200`), `False` otherwise.

**Error handling (FIX REQUIRED, P0):** Must return `False` when `resp.status_code != 200` instead of silently ignoring the error. Never raise an exception — this is a fire-and-forget utility, but the caller must be able to check the result.

---

## 3. Class: `MessengerHookAttachments`

**File:** `src/dooray/MessengerHook.py` (line 67)

### 3.1 Purpose

Builder class for constructing a list of attachment dictionaries to pass to `MessengerHook.send()`.

### 3.2 Constructor

```python
MessengerHookAttachments()
```

**Internal state:**
- `self._attachments: list` — Empty list, populated by `add_attachment()`

### 3.3 `builder()` — Static Factory

```python
@staticmethod
MessengerHookAttachments.builder() -> MessengerHookAttachments
```

Creates and returns a new `MessengerHookAttachments` instance. This is the recommended entry point.

### 3.4 `add_attachment(title=None, title_link=None, text=None, color=None)` — Add Attachment

Adds an attachment to the builder. Returns `self` for chaining.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `title` | `str` or `None` | `None` | Attachment title |
| `title_link` | `str` or `None` | `None` | Clickable URL for the title |
| `text` | `str` or `None` | `None` | Attachment body text |
| `color` | `str` or `None` | `None` | Color name or hex (e.g., `red`, `purple`) |

**Logic:** Delegates to `_create_attachment()`. If the result is not `None`, appends to `self._attachments`.

**Returns:** `self` (for method chaining)

### 3.5 `_create_attachment(title, title_link, text, color)` — Static Helper

```python
@staticmethod
MessengerHookAttachments._create_attachment(title, title_link, text, color) -> dict | None
```

Constructs an attachment dict from non-None parameters. Returns `None` if all parameters are `None`.

**Output dict format (all keys optional):**
```json
{
  "title": "<title>",
  "titleLink": "<title_link>",
  "text": "<text>",
  "color": "<color>"
}
```

### 3.6 `create()` — Build Result

```python
create() -> list[dict]
```

Returns the accumulated list of attachment dicts.

---

## 4. Usage Example

```python
import dooray

# Simple message
hook = dooray.MessengerHook(hook_url="YOUR_HOOK_URL")
hook.send("Hello, World!")

# Message with attachments
attachments = dooray.MessengerHookAttachments.builder()\
    .add_attachment(title='Nice title', title_link='http://dooray.com/', text='Simple text', color='red')\
    .add_attachment(text='Awesome text in purple box', color='purple')\
    .create()

hook.send("Message with attachments", attachments=attachments)
```
