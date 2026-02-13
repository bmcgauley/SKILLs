# API Reference - [API Name]

## Overview

Brief description of what this API does and its main purpose.

**Base URL:** `https://api.example.com/v1`  
**Version:** 1.0.0  
**Last Updated:** [Date]

## Authentication

Describe the authentication method(s) supported by this API.

### API Key Authentication

Include your API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0

This API supports OAuth 2.0 for authentication. See [OAuth setup guide](link) for details.

## Rate Limiting

- **Rate Limit:** 1000 requests per hour
- **Rate Limit Header:** `X-RateLimit-Remaining`
- **Reset Header:** `X-RateLimit-Reset`

When rate limited, the API returns:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "retry_after": 3600
}
```

## Common Response Codes

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request successful |
| `201 Created` | Resource created successfully |
| `400 Bad Request` | Invalid request parameters |
| `401 Unauthorized` | Authentication failed |
| `403 Forbidden` | Access denied |
| `404 Not Found` | Resource not found |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Server error |

## Endpoints

### Resource Collection

#### List Resources

Returns a paginated list of resources.

**Endpoint:** `GET /resources`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Items per page (default: 20, max: 100) |
| `sort` | string | No | Sort field (e.g., `created_at`, `-updated_at`) |
| `filter` | string | No | Filter expression |

**Example Request:**

```bash
curl -X GET "https://api.example.com/v1/resources?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**

```json
{
  "data": [
    {
      "id": "res_123",
      "name": "Example Resource",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10
  }
}
```

---

#### Get Single Resource

Retrieves a specific resource by ID.

**Endpoint:** `GET /resources/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Resource identifier |

**Example Request:**

```bash
curl -X GET "https://api.example.com/v1/resources/res_123" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**

```json
{
  "id": "res_123",
  "name": "Example Resource",
  "description": "Detailed description",
  "metadata": {
    "key": "value"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Response:**

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource with ID res_123 not found"
  }
}
```

---

#### Create Resource

Creates a new resource.

**Endpoint:** `POST /resources`

**Request Body:**

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "metadata": {
    "key": "value"
  }
}
```

**Field Descriptions:**

- `name` (string, required): Resource name (3-100 characters)
- `description` (string, optional): Detailed description (max 500 characters)
- `metadata` (object, optional): Key-value pairs for additional data

**Example Request:**

```bash
curl -X POST "https://api.example.com/v1/resources" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Resource",
    "description": "This is a new resource"
  }'
```

**Success Response (201 Created):**

```json
{
  "id": "res_124",
  "name": "New Resource",
  "description": "This is a new resource",
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Validation Error Response (400 Bad Request):**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "fields": {
      "name": "Name is required",
      "description": "Description exceeds maximum length"
    }
  }
}
```

---

#### Update Resource

Updates an existing resource.

**Endpoint:** `PUT /resources/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Resource identifier |

**Request Body:**

```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "metadata": {
    "key": "value"
  }
}
```

**Note:** Only include fields you want to update.

**Example Request:**

```bash
curl -X PUT "https://api.example.com/v1/resources/res_123" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

**Success Response:**

```json
{
  "id": "res_123",
  "name": "Example Resource",
  "description": "Updated description",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

#### Delete Resource

Deletes a resource permanently.

**Endpoint:** `DELETE /resources/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Resource identifier |

**Example Request:**

```bash
curl -X DELETE "https://api.example.com/v1/resources/res_123" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response (204 No Content):**

No response body.

**Error Response (404 Not Found):**

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource with ID res_123 not found"
  }
}
```

## Webhooks

### Webhook Events

The API can send webhooks for the following events:

| Event | Description |
|-------|-------------|
| `resource.created` | New resource created |
| `resource.updated` | Resource updated |
| `resource.deleted` | Resource deleted |

### Webhook Payload

```json
{
  "id": "evt_123",
  "type": "resource.created",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "id": "res_123",
    "name": "Example Resource"
  }
}
```

### Webhook Security

All webhooks include a signature header for verification:

```http
X-Webhook-Signature: sha256=SIGNATURE
```

Verify the signature using:
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "information"
    }
  }
}
```

### Common Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `INVALID_REQUEST` | Malformed request | Check request format |
| `AUTHENTICATION_REQUIRED` | Missing authentication | Include API key |
| `INVALID_API_KEY` | Invalid or expired key | Check API key |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist | Verify resource ID |
| `VALIDATION_ERROR` | Invalid input data | Check field requirements |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `INTERNAL_ERROR` | Server error | Contact support |

## SDKs and Libraries

Official SDKs are available for:

- [Python](https://github.com/example/python-sdk)
- [JavaScript/Node.js](https://github.com/example/js-sdk)
- [Ruby](https://github.com/example/ruby-sdk)
- [Go](https://github.com/example/go-sdk)

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial API release
- Basic CRUD operations
- Webhook support

### Version 0.9.0 (2024-01-01)
- Beta release
- Limited access

## Support

- **Documentation:** https://docs.example.com
- **Status Page:** https://status.example.com
- **Support Email:** api-support@example.com
- **Community Forum:** https://forum.example.com

## Code Examples

### Python

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.example.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# List resources
response = requests.get(f"{BASE_URL}/resources", headers=headers)
resources = response.json()

# Create resource
data = {"name": "New Resource"}
response = requests.post(f"{BASE_URL}/resources", json=data, headers=headers)
new_resource = response.json()
```

### JavaScript

```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.example.com/v1';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// List resources
fetch(`${BASE_URL}/resources`, { headers })
  .then(res => res.json())
  .then(data => console.log(data));

// Create resource
fetch(`${BASE_URL}/resources`, {
  method: 'POST',
  headers,
  body: JSON.stringify({ name: 'New Resource' })
})
  .then(res => res.json())
  .then(data => console.log(data));
```
