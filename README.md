# Referral Auth Service

Production-ready Django REST API implementing **phone authentication via OTP** and a **referral system**.

The project demonstrates a modern backend architecture including:

* Django + Django REST Framework
* Custom User model
* JWT authentication
* OTP login flow
* Referral system
* PostgreSQL database
* Dockerized deployment
* CI pipeline (GitHub Actions)
* Automated testing with pytest

---

# Features

## Authentication

* Phone number based authentication
* One-time password (OTP) verification
* JWT token issuing (access + refresh)

## Referral System

* Unique invite code for every user
* Invite activation
* Referral tracking

## Production Infrastructure

* PostgreSQL database
* Docker containers
* Gunicorn application server
* Health checks
* CI pipeline with lint + tests

---

# Tech Stack

* Python 3.13
* Django
* Django REST Framework
* PostgreSQL
* SimpleJWT
* DRF Spectacular (OpenAPI)
* Docker
* Poetry
* Pytest
* GitHub Actions

---

# Architecture

The project follows a layered architecture:

views → serializers → services → models

* **Views** handle HTTP requests
* **Serializers** validate API data
* **Services** contain business logic
* **Models** represent database entities

This separation improves maintainability and testability.

---

# Project Structure

```
src/
 ├── apps/
 │   ├── users/
 │   │   ├── models.py
 │   │   ├── views.py
 │   │   ├── views_web.py
 │   │   ├── serializers.py
 │   │   ├── services.py
 │   │   ├── urls.py
 │   │   └── tests/
 │   │
 │   └── core/
 │       └── views.py
 │
 ├── config/
 │   ├── settings/
 │   │   ├── base.py
 │   │   ├── dev.py
 │   │   ├── prod.py
 │   │   └── ci.py
 │   └── urls.py
 │
 └── manage.py
```

---

# Authentication Flow

## Step 1 — Request OTP

```
POST /users/auth/request-code/
```

User sends phone number.
If the user does not exist — the account is created.

### Request

```json
{
  "phone": "+79991234567"
}
```

### Response

```
200 OK
```

```json
{
  "detail": "Verification code sent"
}
```

OTP is generated and stored with TTL.

---

## Step 2 — Verify OTP

```
POST /users/auth/verify-code/
```

### Request

```json
{
  "phone": "+79991234567",
  "code": "123456"
}
```

### Response

```
200 OK
```

```json
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token"
}
```

User becomes **authenticated** and receives JWT tokens.

---

# Profile API

All profile endpoints require authentication.

```
Authorization: Bearer <access_token>
```

---

## Get Profile

```
GET /users/profile/
```

### Response

```json
{
  "phone": "+79991234567",
  "invite_code": "AB12CD",
  "invited_by": "+79990000000",
  "referrals": [
    "+79995555555",
    "+79996666666"
  ]
}
```

---

## Activate Invite Code

```
POST /users/profile/activate-invite/
```

### Request

```json
{
  "invite_code": "AB12CD"
}
```

### Response

```
200 OK
```

```json
{
  "detail": "Invite activated"
}
```

### Errors

Self invite:

```
400 Bad Request
```

```json
{
  "error": "You cannot use your own invite code"
}
```

Invite already activated:

```
400 Bad Request
```

```json
{
  "error": "Invite already used"
}
```

Invalid code:

```
404 Not Found
```

```json
{
  "error": "Invite code not found"
}
```

---

# Health Check

```
GET /health/
```

### Response

```json
{
  "status": "ok"
}
```

Used for:

* Docker healthchecks
* load balancers
* monitoring systems

---

# API Documentation

Swagger UI:

```
/api/docs/
```

ReDoc:

```
/api/redoc/
```

---

# Running Locally (Docker)

Clone repository:

```
git clone https://github.com/yourusername/referral-auth-service
cd referral-auth-service
```

Create environment file:

```
.env.prod
```

Example:

```
SECRET_KEY=secret
DEBUG=False

POSTGRES_DB=referral
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Run containers:

```
docker compose -f docker-compose.prod.yml up -d --build
```

Application will be available at:

```
http://localhost:8000
```

---

# Running Tests

```
pytest
```

Current test coverage:

```
86%
```

Test categories:

* OTP flow
* user creation
* invite activation
* referral logic
* error cases

---

# CI Pipeline

GitHub Actions pipeline includes:

* dependency installation
* isort formatting check
* flake8 lint
* pytest execution
* Docker build

Pipeline stages:

```
format → lint → test → docker
```

---

# Environment Variables

Required environment variables:

```
SECRET_KEY
DEBUG

POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
```

Example configuration is provided in:

```
.env.sample
.env.prod.sample
```

---

# Security Notes

* OTP codes have expiration (TTL)
* JWT authentication
* Invite code cannot be reused
* Self-invite protection
* Secrets stored in environment variables

---

# Author

Backend project demonstrating production-ready Django REST API development.

Built as part of backend engineering portfolio.
