# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

This API uses JWT Bearer token authentication.

### Getting a Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header:
```
Authorization: Bearer eyJ...
```

## Endpoints

### Health

#### GET /health/
Health check endpoint.

**Response:** `200 OK`
```json
{"status": "healthy"}
```

### Auth

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`

#### POST /auth/login
Login and get tokens.

**Request Body:** `application/x-www-form-urlencoded`
- `username`: Email address
- `password`: Password

**Response:** `200 OK`
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user info. Requires authentication.

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Users

#### GET /users/
List all users. Requires superuser.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Max records to return (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

#### GET /users/{user_id}
Get user by ID. Requires authentication.

#### PATCH /users/{user_id}
Update user. Requires authentication.

#### DELETE /users/{user_id}
Delete user. Requires superuser.

### Items

#### GET /items/
List current user's items. Requires authentication.

#### POST /items/
Create new item. Requires authentication.

**Request Body:**
```json
{
  "title": "My Item",
  "description": "Optional description"
}
```

#### GET /items/{item_id}
Get item by ID. Requires authentication.

#### PATCH /items/{item_id}
Update item. Requires ownership or superuser.

#### DELETE /items/{item_id}
Delete item. Requires ownership or superuser.

## Error Responses

```json
{
  "error": "Error message",
  "detail": "Additional details"
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |
