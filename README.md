# DevOps LLM Web Application

A production-grade, containerized Flask application that integrates Groq's LLaMA 3.1 API with SQLite for prompt management and AI-powered response generation. Built with DevOps best practices including CI/CD, Docker multi-stage builds, Nginx reverse proxy, and comprehensive testing.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Architecture

```
┌──────────────┐      ┌────────────────┐      ┌──────────────┐
│   Browser    │─────▶│  Nginx Proxy   │─────▶│  Flask App   │
│   (Client)   │◀─────│  (Port 80)     │◀─────│  (Port 5000) │
└──────────────┘      └────────────────┘      └──────┬───────┘
                                                     │
                                          ┌──────────┴──────────┐
                                          │                     │
                                   ┌──────▼──────┐    ┌────────▼────────┐
                                   │   SQLite    │    │   Groq API      │
                                   │  (Prompts)  │    │  (LLaMA 3.1)   │
                                   └─────────────┘    └─────────────────┘
```

## Tech Stack

| Layer          | Technology                                      |
|----------------|------------------------------------------------|
| **Backend**    | Python 3.11, Flask, Gunicorn                   |
| **LLM**       | Groq API, LLaMA 3.1 8B Instant                |
| **Database**   | SQLite with WAL mode                           |
| **Frontend**   | HTML5, CSS3, Vanilla JavaScript                |
| **Container**  | Docker (multi-stage build), Docker Compose     |
| **Proxy**      | Nginx (reverse proxy, gzip, security headers)  |
| **CI/CD**      | GitHub Actions (lint → test → build → scan)    |
| **Testing**    | Pytest with coverage reporting                 |
| **Quality**    | Black, isort, flake8, pip-audit                |

## Features

- **RESTful API** with structured JSON responses and proper error handling
- **Rate Limiting** — Sliding window rate limiter to prevent API abuse
- **Retry Logic** — Exponential backoff for Groq API failures
- **Health Check** — `/health` endpoint with database and LLM service status
- **Category Filtering** — Prompts organized by topic with frontend filters
- **Request Logging** — Structured logging with latency tracking per request
- **Security** — Non-root Docker user, security headers via Nginx, env-based secrets
- **Multi-stage Docker Build** — Optimized image size for production
- **CI/CD Pipeline** — Automated linting, testing, Docker build, and security scanning

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/devops-llm-project.git
cd devops-llm-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
make install

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the application
make run
# Visit http://localhost:5000
```

### Docker Deployment

```bash
# Build and start all services (App + Nginx)
make docker-up

# Visit http://localhost (port 80 via Nginx)

# View logs
make docker-logs

# Stop services
make docker-down
```

## API Reference

| Method | Endpoint             | Description                     |
|--------|---------------------|---------------------------------|
| GET    | `/`                 | Web interface                   |
| GET    | `/health`           | Health check with service status|
| GET    | `/api/prompts`      | List all prompts                |
| GET    | `/api/prompts/<id>` | Get specific prompt             |
| GET    | `/api/categories`   | List prompt categories          |
| POST   | `/api/generate`     | Generate LLM response           |

### Example: Generate Response

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

```json
{
  "status": "success",
  "data": {
    "prompt_id": 1,
    "response": "AI-generated response...",
    "model": "llama-3.1-8b-instant",
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 312,
      "total_tokens": 337
    },
    "latency_seconds": 1.24
  }
}
```

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and PR to `main`:

```
Lint (Black + isort + flake8)
        │
        ├──▶ Tests (Pytest + Coverage)
        │           │
        │           └──▶ Docker Build + Health Check
        │
        └──▶ Security Scan (pip-audit)
```

## Project Structure

```
devops-llm-project/
├── app/
│   ├── __init__.py          # Package init
│   ├── config.py            # Environment-based configuration
│   ├── database.py          # Database CRUD with connection management
│   ├── llm_service.py       # LLM service with retry logic
│   ├── main.py              # Application factory
│   ├── middleware.py         # Rate limiting, logging, error handlers
│   └── routes.py            # API endpoints and route handlers
├── templates/
│   └── index.html           # Frontend interface
├── tests/
│   └── test_app.py          # Unit tests (health, API, DB, errors)
├── nginx/
│   └── nginx.conf           # Reverse proxy configuration
├── .github/workflows/
│   └── ci-cd.yml            # CI/CD pipeline
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Container orchestration
├── Makefile                 # Developer convenience commands
├── requirements.txt         # Pinned dependencies
├── .env.example             # Environment template
├── .gitignore
├── .dockerignore
└── README.md
```

## Testing

```bash
# Run all tests
make test

# Run with verbose output
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for all options:

| Variable                | Default                  | Description              |
|------------------------|--------------------------|--------------------------|
| `GROQ_API_KEY`         | *required*               | Groq API key             |
| `GROQ_MODEL`           | `llama-3.1-8b-instant`   | LLM model identifier     |
| `FLASK_ENV`            | `development`            | App environment           |
| `RATE_LIMIT_PER_MINUTE`| `30`                     | Max requests per minute   |
| `LOG_LEVEL`            | `INFO`                   | Logging verbosity         |

## License

MIT License — see [LICENSE](LICENSE) for details.
