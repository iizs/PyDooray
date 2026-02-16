# API Reference: {Feature/Service Name}

**Base URL:** `{Current Base URL, e.g., /api/v1}`
**Version:** 1.0.0

## 1. Authentication
All requests must include the API Key in the header.

```bash
Authorization: Bearer <YOUR_API_KEY>
```

## 2. Resources & Endpoints

### 2.1. {Resource Name, e.g., Users}

#### `GET /users`
> Retrieve a list of users.

**Parameters:**

| Name | Type | In | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `page` | int | Query | No | Page number (default: 1) |
| `limit` | int | Query | No | Items per page (default: 20) |

**Response (200 OK):**
```json
{
  "data": [
    { "id": 1, "name": "Alice" },
    { "id": 2, "name": "Bob" }
  ],
  "meta": { "total": 100 }
}
```

#### `POST /users`
> Create a new user.

**Request Body:**

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `username` | string | **Yes** | Unique username (min 3 chars) |
| `email` | string | **Yes** | Valid email address |

**Example Request:**
```bash
curl -X POST [https://api.example.com/v1/users](https://api.example.com/v1/users) \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'
```

**Response (201 Created):**
```json
{
  "id": 101,
  "status": "pending_verification"
}
```

## 3. Error Codes
Common error codes returned by this API.

| Code | Status | Description |
| :--- | :--- | :--- |
| `400` | Bad Request | Invalid parameters or missing fields. |
| `401` | Unauthorized | Missing or invalid API Key. |
| `404` | Not Found | The requested resource does not exist. |
| `500` | Server Error | Internal system failure. |