# AutoApply ATS - Quick Reference Card

## Starting the Application (Windows PowerShell)

### Option 1: Docker (Recommended for Complete Stack)
```powershell
# In project root
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f api

# Access API
Start-Process "http://localhost:8000/docs"

# Seed database
docker-compose exec api alembic upgrade head
# Then manually create seed data via API or run seed.ps1
```

### Option 2: Local Development
```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env if needed (use local postgres/redis)

# Run migrations
alembic upgrade head

# Seed database
python scripts\seed_db.py

# Start API server
uvicorn app.main:app --reload

# In another terminal, start Celery worker
.\venv\Scripts\celery -A app.workers.celery_app worker --loglevel=info

# In another terminal, start Celery beat
.\venv\Scripts\celery -A app.workers.celery_app beat --loglevel=info
```

## Default Credentials
- **Email**: demo@autoapply.ai
- **Password**: password123
- **API Base URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Database**: postgres / password (if using local PostgreSQL)

## Common API Calls (PowerShell)

### Login
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"demo@autoapply.ai","password":"password123"}'

$token = ($response.Content | ConvertFrom-Json).access_token
```

### Get Profile
```powershell
$headers = @{"Authorization" = "Bearer $token"}
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile" `
  -Headers $headers
```

### Create Job
```powershell
$jobData = @{
  title = "Senior Python Engineer"
  company = "TechCorp"
  url = "https://example.com/job"
  raw_jd = "Job description text..."
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/jobs" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $jobData
```

### Extract Job Description
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/jobs/1/extract" `
  -Method POST `
  -Headers $headers
```

### Generate Resume
```powershell
$resumeData = @{
  job_id = 1
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/resumes" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $resumeData
```

## Port Usage
- **8000**: FastAPI (http://localhost:8000)
- **5432**: PostgreSQL
- **6379**: Redis
- **5555**: Celery Flower (if enabled)

## Database Connections (Local)
```
PostgreSQL: postgresql://postgres:password@localhost:5432/autoapply
Redis: redis://localhost:6379
```

## VS Code Debugging
1. Install Python extension (ms-python.python)
2. Create `.vscode/launch.json` with FastAPI config
3. Set breakpoints
4. Press F5 to start debugging

## Environment Variables (.env)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/autoapply
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# LLM Configuration (stub until real integration)
LLM_PROVIDER=openai  # or anthropic
LLM_API_KEY=your-key-here
LLM_MODEL=gpt-4  # or claude-3-opus
LLM_TEMPERATURE=0.7

LOG_LEVEL=INFO
STORAGE_PATH=./storage
```

## File Locations
```
Project Root: c:\Users\Mahesh\projects\JobApply\autoapply-ats

Backend Code: backend/app/
  - main.py (entry point)
  - db/models/ (SQLAlchemy models)
  - schemas/ (Pydantic validation)
  - services/ (business logic)
  - api/routers/ (endpoints)
  - llm/ (LLM pipeline)
  - workers/ (Celery tasks)
  - web/templates/ (HTML)
  - core/ (config, auth)

Tests: backend/tests/
  - test_jd_extraction.py
  - test_resume_validation.py
  - test_matching.py
  - conftest.py

Migrations: backend/alembic/versions/

Scripts: backend/scripts/
  - seed_db.py (Python seeding)
  - seed.ps1 (PowerShell seeding)

Docs: docs/
  - api_complete.md
  - architecture.md
  - ats_rules.md
```

## Testing

### Run All Tests
```powershell
cd backend
pytest tests/ -v
```

### Run Specific Test
```powershell
pytest tests/test_jd_extraction.py -v
```

### Run with Coverage
```powershell
pytest tests/ --cov=app --cov-report=html
```

## Code Quality

### Format Code
```powershell
black app/ tests/ --line-length=100
```

### Lint
```powershell
ruff check app/ tests/
```

### Type Check
```powershell
mypy app/
```

## Stopping Services

### Docker
```powershell
docker-compose down
```

### Local (Ctrl+C)
- API: Press Ctrl+C in API terminal
- Worker: Press Ctrl+C in worker terminal
- Beat: Press Ctrl+C in beat terminal

## Logs and Debugging

### Docker Logs
```powershell
docker-compose logs api          # API logs
docker-compose logs postgres     # Database logs
docker-compose logs redis        # Cache logs
docker-compose logs -f           # Follow all logs
```

### Application Logs
Located in: `backend/logs/` (if configured)

### Database Queries
Enable query logging in `.env`:
```
SQLALCHEMY_ECHO=true
```

## Reset/Clean

### Reset Database
```powershell
# Docker
docker-compose down -v
docker-compose up -d

# Local
# Delete your local PostgreSQL database and recreate
```

### Clear Cache
```powershell
Remove-Item __pycache__ -Recurse -ErrorAction SilentlyContinue
Remove-Item .pytest_cache -Recurse -ErrorAction SilentlyContinue
Remove-Item .coverage -Recurse -ErrorAction SilentlyContinue
```

## Common Issues & Solutions

1. **Port 8000 already in use**
   - Stop other services or use `-p 8001:8000` flag

2. **Database connection failed**
   - Check PostgreSQL is running: `docker-compose ps`
   - Verify DATABASE_URL in .env
   - Run migrations: `alembic upgrade head`

3. **ModuleNotFoundError**
   - Ensure you're in virtual environment: `.\venv\Scripts\Activate.ps1`
   - Reinstall: `pip install -e ".[dev]"`

4. **Celery tasks not running**
   - Check Redis connection: `redis-cli ping` should return PONG
   - Ensure worker is running in another terminal
   - Check logs: `docker-compose logs worker`

5. **JWT token invalid**
   - Token may be expired, re-login
   - SECRET_KEY may have changed, use same key for all instances

## Useful Commands Summary
```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Access database
docker-compose exec postgres psql -U postgres -d autoapply

# View all jobs
docker-compose exec postgres psql -U postgres -d autoapply -c "SELECT * FROM job;"

# Reset everything
docker-compose down -v
docker-compose up -d
```

## Next Steps
1. Run WINDOWS_SETUP.md for complete installation
2. Access http://localhost:8000/docs for interactive API
3. Test with demo credentials
4. Integrate real LLM (OpenAI/Anthropic) in `app/llm/client.py`
5. Implement PDF rendering in `app/services/document_service.py`
6. Deploy to production (v0.2)
