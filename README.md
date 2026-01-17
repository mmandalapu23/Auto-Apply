# AutoApply ATS

AI-powered job application system that imports jobs from job portals and helps manage your job search.

## Features

- **Job Import**: Automatically fetch jobs from Greenhouse job boards
- **Job Management**: Store and organize job postings
- **Web Interface**: Simple UI to browse and view jobs
- **REST API**: Full API for programmatic access

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: Jinja2 templates, vanilla CSS
- **Job Sources**: Greenhouse API

## Quick Start

### Prerequisites

- Python 3.11+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/mmandalapu23/Auto-Apply.git
cd Auto-Apply

# Create virtual environment
cd backend
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Initialize database
python scripts/seed_db.py

# Import jobs from job portals
python scripts/import_jobs.py

# Run server
uvicorn app.main:app --reload --port 8001
```

### Access

- **Web UI**: http://localhost:8001/jobs
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## Project Structure

```
backend/
├── app/
│   ├── api/           # REST API endpoints
│   ├── core/          # Config, security, logging
│   ├── db/            # Database models and session
│   ├── schemas/       # Pydantic request/response models
│   ├── services/      # Business logic
│   └── web/           # Server-rendered UI
├── scripts/           # Utility scripts
└── tests/             # Test suite
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List all jobs (web) |
| GET | `/jobs/{id}` | View job details (web) |
| GET | `/api/v1/jobs` | List jobs (API) |
| POST | `/api/v1/jobs` | Create job |
| POST | `/api/v1/jobs/import` | Import from Greenhouse |
| GET | `/health` | Health check |

## Scripts

```bash
# Seed demo user and sample data
python scripts/seed_db.py

# Import jobs from Greenhouse boards
python scripts/import_jobs.py
```

## Configuration

Environment variables (set in `.env` or shell):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./autoapply.db` | Database connection |
| `SECRET_KEY` | `your-secret-key...` | JWT signing key |
| `DEBUG` | `False` | Enable debug mode |

## License

MIT
