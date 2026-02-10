# [DRIFT] Spec vs Code Discrepancy Report

**Date:** {YYYY-MM-DD}
**Target Component:** {Repo/File Name}
**Severity:** {High/Medium/Low}

## 1. Executive Summary
> Briefly state how much the implementation has deviated from the design.

## 2. Detected Drifts

### 2.1. Interface / API Changes
| Endpoint / Method | Spec Definition | Actual Code Implementation |
| :--- | :--- | :--- |
| `POST /users` | Returns `201 Created` | Returns `200 OK` with JSON |
| `GET /items` | Param `limit` default 10 | Param `limit` default 20 |

### 2.2. Data Model Changes
* **Table `users`:**
  * Spec: `phone_number` (VARCHAR)
  * Code: `phone_number` is REMOVED.
  * Code: Added `mobile_verified` (BOOLEAN).

### 2.3. Logic Changes
> Describe behavior changes.
* *Example:* The Spec required sending an email **before** DB save, but Code sends it **after** DB save asynchronously.

## 3. Recommendation
* [ ] **Update Spec:** The code change is valid/intentional. Update docs.
* [ ] **Fix Code:** The code is wrong (Bug). Revert to Spec design.