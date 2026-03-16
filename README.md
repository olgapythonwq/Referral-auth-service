# Referral Auth Service

Production-ready Django REST API implementing **phone authentication via OTP** and a **referral system**.

The project demonstrates a modern backend architecture including:

* Django + Django REST Framework
* Custom User model
* JWT authentication
* OTP login flow
* Referral system
* PostgreSQL
* Docker
* CI pipeline (GitHub Actions)
* Automated tests (pytest)

---

# Features

### Authentication

* Phone number based authentication
* One-time password (OTP) verification
* JWT token issuing

### Referral system

* Unique invite code for every user
* Invite activation
* Referral tracking

### Production infrastructure

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

# Project Structure

```
src/
 ├── apps/
 │   ├── users
 │   │   ├── models.py
 │   │   ├── views.py
 │   │   ├── serializers.py
 │   │   ├── services.py
 │   │   └── tests
 │   └── core
 │
 ├── config
 │   ├── settings
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

### Step 1 — Request OTP

```
POST /auth/request-code/
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

# Verify OTP

```
POST /auth/verify-code/
```

### Request

```json
{
  "phone": "+79991234567",
  "code": "1234"
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

User becomes **active** and receives JWT tokens.

---

# Profile API

Requires JWT authentication.

```
Authorization: Bearer <access_token>
```

---

# Get Profile

```
GET /profile/
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

# Activate Invite Code

```
POST /profile/activate-invite/
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

# OpenAPI Documentation

Swagger UI:

```
/api/schema/swagger-ui/
```

ReDoc:

```
/api/schema/redoc/
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

API will be available at:

```
http://localhost:8000
```

---

# Running Tests

```
pytest
```

Test coverage target:

```
75–85%
```

Test categories:

* OTP flow
* User creation
* Invite activation
* Referral listing
* Error cases

---

# CI Pipeline

GitHub Actions pipeline includes:

* dependency installation
* flake8 lint
* migrations
* pytest
* Docker build
* deployment

Pipeline stages:

```
lint → test → docker → deploy
```

---

# Security Notes

* OTP codes have TTL
* JWT authentication
* Invite code cannot be reused
* Self-invite protection
* Environment variables for secrets

---

# Author

Backend project demonstrating production-ready Django REST API development.

Built as part of backend engineering portfolio.

