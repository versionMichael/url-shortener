# URL Shortener API

A production-ready URL shortening REST API built with FastAPI, PostgreSQL, Redis, JWT authentication, and Docker.

The API allows authenticated users to create, manage, and track shortened URLs, while public users can access shortened URLs without authentication.

## Live Demo

- API: https://url-shortener-production-2412.up.railway.app
- Swagger Documentation: https://url-shortener-production-2412.up.railway.app/docs

## Features

- User registration and JWT authentication
- Secure password hashing with Argon2
- Create shortened URLs
- Public URL redirects
- URL expiration
- Click tracking
- Redis URL caching
- Redis-based IP rate limiting
- URL ownership and authorization
- PostgreSQL database
- Async database operations
- Pydantic request validation
- Automated tests with Pytest
- Docker containerization
- Docker Compose for local development
- Persistent PostgreSQL storage with Docker volumes
- Railway deployment

## Tech Stack

- **Python 3.14**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Psycopg 3**
- **Redis**
- **JWT**
- **pwdlib / Argon2**
- **Pydantic**
- **Pytest**
- **Docker**
- **Docker Compose**
- **Railway**

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT token | No |

### URLs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/urls` | Create a shortened URL | Yes |
| GET | `/urls` | Get the authenticated user's URLs | Yes |
| GET | `/urls/{id}` | Get a specific URL | Yes |
| DELETE | `/urls/{id}` | Delete a URL | Yes |

### Redirect

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/{short_code}` | Redirect to the original URL | No |

The redirect endpoint also handles click tracking, caching, URL expiration, and rate limiting.

## Using a Shortened URL

After creating a shortened URL, the API returns a `short_code`.

To use the shortened URL, place the `short_code` at the end of the API's base URL:

```text
https://url-shortener-production-2412.up.railway.app/{short_code}
```

For example, if the API returns:

```text
short_code: abc123
```

Your shortened URL would be:

```text
https://url-shortener-production-2412.up.railway.app/abc123
```

Opening the shortened URL will redirect you to the original website.

## Authentication

The API uses JWT bearer authentication.

Passwords are securely hashed before being stored in PostgreSQL.

Protected endpoints require an access token:

```text
Authorization: Bearer <access_token>
```

Users can only access and delete their own URLs.

## Redis

Redis is used for two purposes:

### URL Caching

Frequently accessed shortened URLs are cached in Redis to reduce database lookups.

```text
url:{short_code}
```

### Rate Limiting

Public redirects are rate limited by IP address.

The current configuration allows:

```text
10 requests per IP address
within a 60-second window
```

Requests exceeding the limit receive:

```text
429 Too Many Requests
```

## Database

PostgreSQL is the source of truth for application data.

The main URL model stores:

- ID
- User ID
- Short code
- Original URL
- Click count
- Creation timestamp
- Expiration timestamp

Users are associated with the URLs they create.

## Async Architecture

The application uses FastAPI's asynchronous architecture with:

- Async SQLAlchemy
- Psycopg 3
- Async Redis

This allows the application to efficiently handle I/O-bound operations such as database and Redis requests without blocking the worker while waiting for those operations to complete.

## Testing

The project includes automated tests covering:

- User registration
- Duplicate registration
- Login
- Authentication failures
- Protected endpoints
- Database connectivity
- Database isolation
- URL creation
- URL retrieval
- URL deletion
- URL ownership
- Redirect behavior
- URL expiration
- Click tracking
- Redis caching
- Rate limiting

Current test result:

```text
32 passed
```

Run the test suite with:

```bash
pytest
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/versionMichael/url-shortener.git
cd url-shortener
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/url_shortener
TEST_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/url_shortener_test
SECRET_KEY=YOUR_SECRET_KEY
```

`REDIS_URL` is optional for local development. If it is not set, the application defaults to:

```text
redis://localhost:6379/0
```

### 5. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Running with Docker Compose

Make sure Docker Desktop is running.

Start the application and PostgreSQL:

```bash
docker compose up
```

The Docker Compose setup includes:

- FastAPI
- PostgreSQL
- PostgreSQL healthcheck
- Persistent PostgreSQL volume

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Stop the containers with:

```bash
docker compose down
```

The PostgreSQL data volume is preserved when using `docker compose down`.

## Project Structure

```text
url-shortener/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── url.py
│   │   └── user.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── redirect.py
│   │   └── urls.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── url.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── cache.py
│   │   ├── rate_limit.py
│   │   └── url.py
│   │
│   ├── database.py
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_cache.py
│   ├── test_database.py
│   ├── test_isolation.py
│   ├── test_rate_limit.py
│   ├── test_redirects.py
│   └── test_urls.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
└── requirements.txt
```

## Deployment

The application is deployed using Railway.

Production architecture:

```text
                    ┌─────────────────┐
                    │     Client      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │    Railway      │
                    └───────┬─────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐
        │   PostgreSQL    │   │      Redis      │
        │     Railway     │   │     Railway     │
        └─────────────────┘   └─────────────────┘
```

PostgreSQL stores persistent application data, while Redis handles caching and rate limiting.

## Security

- Passwords are never stored in plaintext.
- JWT authentication protects private endpoints.
- Users can only manage their own URLs.
- Secrets are provided through environment variables.
- `.env` is excluded from Git.
- `.dockerignore` prevents `.env` from being copied into Docker images.

## Author

Michael

GitHub: https://github.com/versionMichael
