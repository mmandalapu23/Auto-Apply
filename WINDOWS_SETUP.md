# AutoApply ATS - Windows Setup Guide

## Quick Start (Windows PowerShell)

### Prerequisites
- Windows 10+ or Windows Server 2019+
- PowerShell 5.1+ (usually pre-installed)
- Docker Desktop for Windows (or Docker + Docker Compose)
- Python 3.10+ (from python.org or Windows Store)
- Git for Windows (optional but recommended)

### Step 1: Clone and Navigate to Project

```powershell
cd C:\Users\YourName\projects\JobApply\autoapply-ats
```

### Step 2: Start Database and Cache Services

```powershell
# Start PostgreSQL and Redis containers
docker-compose up -d

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME              STATUS
postgres          Up (healthy)
redis             Up (healthy)
```

### Step 3: Setup Python Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# For PowerShell:
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -e ".[dev]"
```

### Step 4: Configure Environment

```powershell
# Copy example to actual .env file
Copy-Item ..\..\.env.example ..\..\.env

# Edit .env with your settings (or keep defaults for MVP)
# notepad ..\..\.env
```

### Step 5: Create Database and Run Migrations

```powershell
# Navigate to backend if not already there
cd C:\Users\YourName\projects\JobApply\autoapply-ats\backend

# Run migrations
alembic upgrade head

# You should see: "Running upgrade -> ... head"
```

### Step 6: Seed Sample Data

```powershell
# From backend directory
.\..\..\scripts\seed.ps1

# Expected output:
# ✓ Created user: demo@autoapply.ai
# ✓ Created profile for John Doe
# ✓ Added 2 work experiences
# ✓ Added 2 projects
# ✓ Added 2 education entries
# ✓ Added 15 skills
# ✓ Added sample job posting
# ✅ Database seeding completed successfully!
```

### Step 7: Start API Server

**Option A: Simple (Single Terminal)**
```powershell
# From backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# Press Ctrl+C to stop
```

**Option B: Background (Multiple Terminals)**

Terminal 1 - API:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Celery Worker:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info
```

Terminal 3 - Celery Beat (Scheduler):
```powershell
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app beat --loglevel=info
```

### Step 8: Test the API

```powershell
# Test health check
Invoke-WebRequest -Uri http://localhost:8000/health

# Should return: {"status":"ok"}
```

### Step 9: Access the API

- **API Swagger Docs**: http://localhost:8000/docs
- **ReDoc Docs**: http://localhost:8000/redoc

## Database Credentials (MVP Defaults)

From `.env.example`:
- **Database URL**: `postgresql://user:password@localhost:5432/autoapply`
- **Redis URL**: `redis://localhost:6379/0`

## Demo User (After Seeding)

- **Email**: `demo@autoapply.ai`
- **Password**: `password123`

## Development Commands

### Run Tests

```powershell
# From backend directory with venv activated
pytest                    # Run all tests
pytest -v                # Verbose output
pytest --cov             # With coverage report
pytest tests/test_jd_extraction.py::test_jd_extract_schema  # Specific test
```

### Code Formatting

```powershell
# Format code
black app/

# Lint code
ruff check app/
```

### Database Migrations

```powershell
# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Troubleshooting

### Issue: "cannot open shared object file"
**Solution**: Ensure PostgreSQL client libraries are available
```powershell
# Install from Docker if needed:
docker exec autoapply-ats-postgres-1 psql --version
```

### Issue: "Address already in use"
**Solution**: Port 8000 or 5432 is already in use
```powershell
# Find and kill process on port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess | % {Stop-Process $_.OwningProcess}

# Or use different port:
uvicorn app.main:app --port 8001
```

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution**: Ensure you're in the backend directory and venv is activated
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

### Issue: Database connection fails
**Solution**: Check Docker containers and wait for initialization
```powershell
docker-compose logs postgres
docker-compose logs redis
docker-compose restart  # Restart if needed
```

## Docker Commands

```powershell
# View running containers
docker-compose ps

# View logs
docker-compose logs -f postgres   # Follow logs

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
```

## VS Code Setup

1. Install Python extension
2. Open folder: `C:\Users\YourName\projects\JobApply\autoapply-ats`
3. Select interpreter: `./backend/venv/Scripts/python.exe`
4. F5 to debug (uses `.vscode/launch.json`)

### Debug Configuration

The `.vscode/launch.json` includes configurations for:
- **FastAPI Debug**: Run with breakpoints and hot reload
- **Celery Worker Debug**: Debug async tasks
- **Run Tests**: Run pytest with debugger

## Architecture Quick Reference

```
autoapply-ats/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── api/                 # REST endpoints
│   │   ├── db/models/           # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── llm/                 # LLM orchestration
│   │   ├── workers/             # Celery tasks
│   │   ├── web/                 # HTML templates
│   │   └── core/                # Config, security, logging
│   ├── tests/                   # Pytest test files
│   ├── pyproject.toml           # Dependencies
│   └── alembic/                 # DB migrations
├── docker-compose.yml           # PostgreSQL + Redis
├── scripts/                      # Setup/seed scripts
└── docs/                        # Documentation
```

## API Endpoints (All require JWT Bearer token)

### Auth
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Profile
- `GET /api/v1/profile` - Get user profile
- `PUT /api/v1/profile` - Update profile

### Jobs
- `POST /api/v1/jobs` - Create job posting
- `GET /api/v1/jobs` - List jobs
- `GET /api/v1/jobs/{id}` - Get job details
- `POST /api/v1/jobs/{id}/extract` - Extract JD structure
- `POST /api/v1/jobs/{id}/match` - Get match score

### Resumes
- `POST /api/v1/resumes` - Generate resume
- `GET /api/v1/resumes/{id}` - Get resume details
- `GET /api/v1/resumes/{id}/pdf` - Get PDF export

### Applications
- `POST /api/v1/applications` - Create application
- `GET /api/v1/applications` - List applications
- `GET /api/v1/applications/{id}` - Get application details
- `PUT /api/v1/applications/{id}` - Update status

## Next Steps

1. **Test the API**: Use Swagger UI at http://localhost:8000/docs
2. **Generate your first resume**: 
   - Register/login with demo account
   - Create/edit profile
   - Add a job posting
   - Click "Generate Resume"
3. **Explore the code**: Each service is well-documented
4. **Run tests**: `pytest` to ensure everything works
5. **Customize**: Modify LLM provider, add real OpenAI/Anthropic API calls

## Production Deployment

For production, you would:
1. Use proper secrets management (AWS Secrets Manager, HashiCorp Vault)
2. Add authentication/rate limiting middleware
3. Deploy via Docker to cloud (AWS ECS, GCP, Azure)
4. Use managed database (RDS, Cloud SQL)
5. Add monitoring/logging (CloudWatch, DataDog)
6. Enable HTTPS/TLS
7. Add request validation and error handling

See `docs/deployment.md` for details (future).

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Check error in VS Code Debug console
3. Test individual endpoints with curl/Postman
4. Review test files for usage examples

Good luck! 🚀
