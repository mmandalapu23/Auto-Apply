# AutoApply ATS - AI-Powered Job Application Automation

A complete MVP system for automating job applications with AI-driven resume tailoring. Built with **FastAPI**, **PostgreSQL**, **Celery**, and **LLM orchestration** with strict evidence-grounding to prevent fabrication.

## 🎯 Features

### Core Functionality
- ✅ **User Profiles**: Store background, experience, projects, education, skills
- ✅ **Job Intake**: Add job descriptions by pasting text or URL
- ✅ **JD Extraction**: Parse job requirements (skills, responsibilities, keywords)
- ✅ **Evidence Mapping**: Ground resume bullets in user-provided evidence
- ✅ **Resume Generation**: AI-driven tailored resumes with no fabrication
- ✅ **Match Scoring**: Job-candidate compatibility scoring
- ✅ **ATS Formatting**: Plain text and PDF exports
- ✅ **Application Queue**: Prepare applications for submission (no auto-submit to preserve compliance)
- ✅ **Audit Logging**: Track all generation and queue actions
- ✅ **Task Scheduling**: Daily application queuing via Celery Beat

### Technical Highlights
- 🏗️ **Modular Monolith**: 8 independent modules (auth, profiles, jobs, matching, documents, llm_orchestrator, applications, audit, workers)
- 🔐 **JWT Authentication**: Secure email/password auth with token-based API
- 🗄️ **SQLAlchemy 2.x + Alembic**: Type-safe ORM with database versioning
- 📦 **Celery + Redis**: Async task processing and caching
- 🤖 **LLM Pipeline**: Multi-step orchestration with schema validation
- 📊 **Pydantic Schemas**: Request/response validation everywhere
- 🧪 **Pytest Suite**: Unit tests for core logic
- 🐳 **Docker Compose**: PostgreSQL + Redis + API + Workers in one command
- 🪟 **Windows-First DX**: Full PowerShell support, VS Code debugging

## 📋 Project Structure

```
autoapply-ats/
├── backend/                    # Main FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── api/
│   │   │   ├── router.py       # Main router (v1 prefix)
│   │   │   ├── deps.py         # JWT auth, DB session injection
│   │   │   └── routers/        # Domain-specific routers
│   │   │       ├── auth.py
│   │   │       ├── profile.py
│   │   │       ├── jobs.py
│   │   │       ├── resumes.py
│   │   │       └── applications.py
│   │   ├── db/
│   │   │   ├── base.py         # ORM base class
│   │   │   ├── session.py      # DB connection
│   │   │   └── models/         # SQLAlchemy models
│   │   │       ├── user.py
│   │   │       ├── profile.py
│   │   │       ├── job.py
│   │   │       ├── resume.py
│   │   │       ├── application.py
│   │   │       └── audit.py
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic (pure functions)
│   │   │   ├── auth_service.py
│   │   │   ├── profile_service.py
│   │   │   ├── job_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── matching_service.py
│   │   │   ├── document_service.py
│   │   │   ├── audit_service.py
│   │   │   └── application_service.py
│   │   ├── llm/                # LLM orchestration
│   │   │   ├── client.py       # LLM provider adapter (stub → OpenAI/Anthropic)
│   │   │   ├── pipeline.py     # Multi-step pipeline with grounding
│   │   │   ├── validators.py   # Resume validation rules
│   │   │   └── prompts/        # Jinja2 prompt templates
│   │   ├── workers/            # Celery tasks
│   │   │   ├── celery_app.py
│   │   │   ├── tasks.py        # Async task definitions
│   │   │   └── schedules.py    # Beat schedules
│   │   ├── documents/
│   │   │   └── templates/      # Jinja2 templates
│   │   ├── web/
│   │   │   ├── templates/      # HTML templates (server-rendered MVP)
│   │   │   └── static/         # CSS, JS
│   │   ├── core/
│   │   │   ├── config.py       # .env settings
│   │   │   ├── security.py     # JWT, password hashing
│   │   │   └── logging.py      # Logging config
│   │   └── utils/
│   ├── tests/
│   │   ├── conftest.py         # Pytest fixtures
│   │   ├── test_jd_extraction.py
│   │   ├── test_resume_validation.py
│   │   └── test_matching.py
│   ├── pyproject.toml          # Dependencies (hatch/pip)
│   ├── alembic.ini             # DB migration config
│   ├── Dockerfile              # Container image
│   └── requirements.txt         # Frozen deps (optional)
├── scripts/
│   ├── dev.ps1                 # PowerShell dev script
│   ├── seed.ps1                # Database seeding
│   └── wait_for_db.py          # Health check
├── docker-compose.yml          # Services: postgres, redis, api, worker, beat
├── .vscode/
│   ├── launch.json             # Debug configurations
│   └── settings.json           # IDE settings
├── docs/
│   ├── api_complete.md         # Full API reference
│   ├── architecture.md         # System design
│   ├── ats_rules.md           # Resume formatting rules
│   └── deployment.md           # Production checklist (planned)
├── WINDOWS_SETUP.md            # Complete Windows setup guide
└── README.md                   # This file
```

## 🚀 Quick Start (Windows PowerShell)

### Prerequisites
- Windows 10+ / Windows Server 2019+
- PowerShell 5.1+
- Python 3.10+
- Docker Desktop for Windows

### 1. Clone Repository
```powershell
cd C:\Users\YourName\projects\JobApply\autoapply-ats
```

### 2. Start Services
```powershell
docker-compose up -d
# Wait ~10 seconds for postgres to initialize
```

### 3. Setup Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 4. Create Database
```powershell
# Create tables
alembic upgrade head

# Seed sample data
..\..\scripts\seed.ps1
```

### 5. Run API
```powershell
uvicorn app.main:app --reload
# API running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

For detailed setup, see [WINDOWS_SETUP.md](WINDOWS_SETUP.md).

## 📚 Core Concepts

### LLM Pipeline (Grounded, No Fabrication)

The system uses a strict 4-step pipeline:

```python
# Step 1: Extract JD
jd_structured = extract_jd(raw_jd_text)
# Output: responsibilities[], must_have_skills[], keywords[], ...

# Step 2: Map Evidence
evidence_map = map_evidence(user_profile, jd_structured)
# Output: matched_items (with IDs), missing_items

# Step 3: Generate Resume
resume = generate_resume(profile, jd_structured, evidence_map)
# Output: Every bullet has evidence_refs[] OR marked NEEDS_USER_INPUT

# Step 4: Validate
passed, issues = validate_resume(resume)
# Checks: no fabrication, ATS formatting, date consistency
```

### Evidence Grounding

Every resume bullet includes evidence references:
```python
{
  "text": "Led team of 10 engineers building microservices",
  "evidence_refs": [
    {
      "type": "experience",
      "id": 123,       # ID from user profile
      "bullet_idx": 0,
      "text": "original evidence from profile"
    }
  ]
}
```

If we can't find evidence, we mark it:
```python
{
  "text": "Kubernetes expert",
  "needs_user_input": "skill_not_found_in_profile"
}
```

### Authentication

JWT-based authentication:
```
1. POST /auth/register or /auth/login
2. Get access_token response
3. All endpoints: Authorization: Bearer <token>
4. Token includes user_id and email
```

### Database Models

```
User
├── Profile (1:1)
│   ├── Experience (1:many)
│   ├── Project (1:many)
│   ├── Education (1:many)
│   └── Skill (1:many)
├── Job (1:many)
│   └── Resume (1:many)
│       └── ResumeBullet (1:many)
├── Application (1:many)
└── AuditLog (1:many)
```

## 🔌 API Endpoints

All endpoints require JWT `Bearer token` (except `/auth/register` and `/auth/login`).

### Auth
- `POST /api/v1/auth/register` - Register user
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
- `POST /api/v1/resumes` - Generate resume for job
- `GET /api/v1/resumes/{id}` - Get resume details
- `GET /api/v1/resumes/{id}/pdf` - Get PDF export

### Applications
- `POST /api/v1/applications` - Create application
- `GET /api/v1/applications` - List applications
- `GET /api/v1/applications/{id}` - Get application
- `PUT /api/v1/applications/{id}` - Update status

See [docs/api_complete.md](docs/api_complete.md) for full documentation with examples.

## 🧪 Testing

```powershell
cd backend

# Run all tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_jd_extraction.py::test_jd_extract_schema -v
```

### Test Coverage
- ✅ JD extraction schema validation
- ✅ Resume validation (evidence grounding)
- ✅ Matching score calculation
- ✅ Evidence mapping logic

## 🐳 Docker Commands

```powershell
# Start all services (postgres, redis, api, worker, beat)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# View container status
docker-compose ps
```

## 📝 Database Migrations

```powershell
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View migration history
alembic history
```

## Demo User (After Seeding)

```
Email: demo@autoapply.ai
Password: password123
```

The seed script creates:
- 1 demo user with complete profile
- 2 work experiences
- 2 projects
- 2 education entries
- 15 skills
- 1 sample job posting

Perfect for testing the full workflow!

## 🎓 Workflow Example

1. **Register/Login**
   ```
   POST /auth/register
   POST /auth/login → get token
   ```

2. **Setup Profile**
   ```
   PUT /profile (add experiences, projects, skills)
   ```

3. **Add Job**
   ```
   POST /jobs (paste job description)
   ```

4. **Check Match**
   ```
   POST /jobs/{id}/match → see match score, missing requirements
   ```

5. **Generate Resume**
   ```
   POST /resumes (generates tailored resume)
   GET /resumes/{id}/pdf (download)
   ```

6. **Create Application**
   ```
   POST /applications (marks as READY_FOR_REVIEW)
   ```

7. **Review & Submit**
   ```
   GET /applications (see queue)
   PUT /applications/{id} (change status to SUBMITTED)
   ```

## 🔒 Compliance & Safety

✅ **No ToS Violations**: MVP only prepares applications, doesn't auto-submit

✅ **No Fabrication**: Every resume bullet must be grounded in user-provided evidence

✅ **Audit Trail**: All generation and queue actions logged with timestamps

✅ **User Control**: User explicitly approves each application before submission

## 🛣️ Roadmap (v0.2+)

- [ ] Real LLM integration (OpenAI/Anthropic)
- [ ] React frontend (replace server-rendered HTML)
- [ ] LinkedIn/Indeed auto-apply integration
- [ ] Job board webhook ingestion
- [ ] Advanced matching algorithms
- [ ] Cover letter generation
- [ ] Multi-resume templates
- [ ] Bulk job import
- [ ] Analytics dashboard

## 🏗️ Architecture Decisions

### Why Monolith?
- Easier to deploy and maintain for MVP
- Easy to split into microservices later
- Shared database transactions for consistency

### Why Celery + Redis?
- Async task processing (resume generation, PDF rendering)
- Reliable task queue for application scheduling
- Caching for frequently accessed data

### Why Evidence Grounding?
- Prevents AI hallucination/fabrication
- Maintains credibility with ATS and recruiters
- Clear audit trail for compliance

### Why No Auto-Submit?
- Legal compliance (ToS of job boards)
- User maintains control
- Can review generated resume first

## 📖 Documentation

- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Complete setup guide
- [docs/api_complete.md](docs/api_complete.md) - Full API reference
- [docs/architecture.md](docs/architecture.md) - System design
- [docs/ats_rules.md](docs/ats_rules.md) - Resume formatting rules

## 🤝 Code Quality

- ✅ Type hints everywhere (Pydantic + SQLAlchemy)
- ✅ Dependency injection (get_db, get_current_user)
- ✅ Service layer separation (business logic)
- ✅ Error handling with HTTPException
- ✅ Logging throughout
- ✅ pytest fixtures for testing
- ✅ Black + Ruff for code formatting

## 💡 Key Files to Understand

1. **app/main.py** - FastAPI app setup
2. **app/llm/pipeline.py** - Core grounding logic
3. **app/db/models/** - Data structures
4. **app/services/** - Business logic
5. **app/api/routers/** - API endpoints
6. **app/workers/tasks.py** - Async jobs

## 🆘 Troubleshooting

### Docker issues
```powershell
# Check logs
docker-compose logs postgres
docker-compose logs redis

# Restart
docker-compose down -v
docker-compose up -d
```

### Database issues
```powershell
# Reset database
alembic downgrade base
alembic upgrade head
.\..\..\scripts\seed.ps1
```

### Port already in use
```powershell
# Find and kill process
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess | % {Stop-Process $_.OwningProcess}
```

See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for more troubleshooting.

## 📄 License

Open source - use and modify freely for educational purposes.

## 🚀 Next Steps

1. Complete the quick start above
2. Explore API via Swagger: http://localhost:8000/docs
3. Try the demo workflow
4. Customize LLM prompts in `app/llm/client.py`
5. Integrate real LLM (OpenAI/Anthropic)
6. Build frontend React app
7. Deploy to cloud (AWS/GCP/Azure)

---

**Built with ❤️ for developers who want to automate tedious job applications responsibly.**

