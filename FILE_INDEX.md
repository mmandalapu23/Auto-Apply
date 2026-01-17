# AutoApply ATS - Complete File Index

## Project Root Files
```
autoapply-ats/
├── README.md                           # 400+ line project overview
├── QUICK_REFERENCE.md                  # Command reference and API examples
├── WINDOWS_SETUP.md                    # Windows-specific setup guide (11 sections, 800+ lines)
├── DEPLOYMENT_CHECKLIST.md             # Pre-deployment verification checklist
├── MVP_COMPLETE.md                     # Detailed MVP completion status
├── dev_server.py                       # Development server launcher
├── docker-compose.yml                  # Multi-service orchestration
├── Dockerfile                          # Backend container image
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore patterns
├── pyproject.toml                      # Python project configuration
├── .github/
│   └── workflows/
│       └── tests.yml                   # GitHub Actions CI/CD pipeline
└── docs/
    ├── api_complete.md                 # 600+ line API reference with examples
    ├── architecture.md                 # System architecture overview
    └── ats_rules.md                    # ATS resume formatting rules
```

## Backend Application (`backend/`)

### Entry Point
```
backend/
└── app/
    ├── __init__.py                     # Package marker
    └── main.py                         # FastAPI application entry point
                                        # - CORS middleware setup
                                        # - Router registration
                                        # - Health check endpoint
                                        # - Logging initialization
```

### Configuration (`backend/app/core/`)
```
app/core/
├── __init__.py                         # Package marker
├── config.py                           # Settings class (Pydantic BaseSettings)
│                                       # - DATABASE_URL, REDIS_URL
│                                       # - SECRET_KEY, ALGORITHM
│                                       # - LLM configuration
│                                       # - Storage paths, log levels
├── security.py                         # Authentication utilities
│                                       # - hash_password()
│                                       # - verify_password()
│                                       # - create_access_token()
│                                       # - decode_access_token()
└── logging.py                          # Logging configuration
```

### Database (`backend/app/db/`)
```
app/db/
├── __init__.py
├── database.py                         # SQLAlchemy engine, session factory
│                                       # - SessionLocal
│                                       # - get_db() context manager
├── models/
│   ├── __init__.py
│   ├── base.py                         # Base model with timestamps
│   ├── user.py                         # User(id, email, hashed_password, full_name, is_active, timestamps)
│   ├── profile.py                      # Profile(1:1 User) with education, university, summary
│   │                                   # Relationships: Experience, Project, Education, Skill (1:many)
│   ├── experience.py                   # Experience(profile_id, title, company, dates, description, technologies[])
│   ├── project.py                      # Project(profile_id, title, description, url, technologies[])
│   ├── education.py                    # Education(profile_id, school, degree_type, field, graduation_year)
│   ├── skill.py                        # Skill(profile_id, name, category, proficiency_level, is_endorsed)
│   ├── job.py                          # Job(user_id, title, company, url, raw_jd, extracted_data JSON)
│   ├── resume.py                       # Resume(job_id, structured_data JSON, ats_text, validation_passed JSON, pdf_path)
│   │                                   # Relationship: ResumeBullet (1:many)
│   ├── resume_bullet.py                # ResumeBullet(resume_id, category, text, evidence_refs[], needs_user_input)
│   ├── application.py                  # Application(job_id, status enum, match_score JSON, missing_requirements JSON)
│   └── audit_log.py                    # AuditLog(user_id, action, resource_type, resource_id, details JSON, metadata JSON)
```

### API Layer (`backend/app/api/`)
```
app/api/
├── __init__.py
├── deps.py                             # Dependency injection
│                                       # - get_db(): SessionLocal
│                                       # - get_current_user(): User from JWT
├── router.py                           # Main APIRouter (/api/v1)
│                                       # - Includes all sub-routers
└── routers/
    ├── __init__.py
    ├── auth.py                         # Authentication endpoints
    │                                   # - POST /auth/register
    │                                   # - POST /auth/login
    ├── profile.py                      # Profile management
    │                                   # - GET /profile
    │                                   # - PUT /profile
    ├── jobs.py                         # Job posting management
    │                                   # - POST /jobs (create)
    │                                   # - GET /jobs (list)
    │                                   # - GET /jobs/{id} (detail)
    │                                   # - POST /jobs/{id}/extract (LLM extraction)
    │                                   # - POST /jobs/{id}/match (match scoring)
    ├── resumes.py                      # Resume generation and export
    │                                   # - POST /resumes (generate)
    │                                   # - GET /resumes/{id}
    │                                   # - GET /resumes/{id}/pdf
    └── applications.py                 # Application tracking
                                        # - POST /applications (create)
                                        # - GET /applications (list)
                                        # - GET /applications/{id}
                                        # - PUT /applications/{id} (update status)
```

### Schemas (`backend/app/schemas/`)
```
app/schemas/
├── __init__.py
├── auth.py                             # Auth schemas
│                                       # - RegisterRequest(email, password, full_name)
│                                       # - LoginRequest(email, password)
│                                       # - TokenResponse(access_token, token_type)
│                                       # - TokenPayload(sub, exp)
├── profile.py                          # Profile schemas (19 classes)
│                                       # - SkillSchema, ExperienceSchema, ProjectSchema
│                                       # - EducationSchema, ProfileSchema
│                                       # - ProfileUpdateRequest
├── job.py                              # Job schemas
│                                       # - JobCreateRequest(title, company, url, raw_jd)
│                                       # - JobSchema, JobDetailSchema
├── jd.py                               # JD extraction schemas
│                                       # - JDExtractRequest, JDStructuredSchema
│                                       # - ResponsibilitySchema
│                                       # - EvidenceRefSchema, EvidenceMapSchema
├── resume.py                           # Resume schemas
│                                       # - ResumeBulletSchema(with evidence_refs)
│                                       # - ResumeStructuredSchema
│                                       # - GenerateResumeRequest, ResumePDFRequest
├── application.py                      # Application schemas
│                                       # - ApplicationSchema, ApplicationCreateRequest
│                                       # - ApplicationStatusUpdateRequest
└── matching.py                         # Matching schemas
                                        # - MatchingScoreSchema
                                        # - MissingRequirementSchema
```

### Services (`backend/app/services/`)
```
app/services/
├── __init__.py                         # Exports all services
├── auth_service.py                     # Authentication service
│                                       # - register_user()
│                                       # - login_user()
│                                       # - verify_password()
│                                       # - get_user_by_id()
├── profile_service.py                  # Profile management
│                                       # - get_or_create_profile()
│                                       # - get_profile()
│                                       # - update_profile()
│                                       # - profile_to_schema()
├── job_service.py                      # Job management
│                                       # - create_job()
│                                       # - get_job()
│                                       # - list_jobs()
│                                       # - update_extracted_data()
├── resume_service.py                   # Resume management
│                                       # - create_resume()
│                                       # - get_resume()
│                                       # - update_pdf_path()
│                                       # - update_validation()
├── matching_service.py                 # Match scoring
│                                       # - calculate_match_score()
├── document_service.py                 # Document rendering
│                                       # - render_resume_html()
│                                       # - render_resume_ats_text()
│                                       # - render_resume_pdf()
├── audit_service.py                    # Audit logging
│                                       # - log_action()
│                                       # - get_logs()
└── application_service.py              # Application tracking
                                        # - create_application()
                                        # - get_application()
                                        # - update_status()
```

### LLM Orchestration (`backend/app/llm/`)
```
app/llm/
├── __init__.py
├── client.py                           # LLM client (stub for OpenAI/Anthropic)
│                                       # - extract_jd(raw_jd) → JDStructuredSchema
│                                       # - generate_resume_text() stub
│                                       # - Internal extraction methods
├── pipeline.py                         # 4-step grounding pipeline
│                                       # - extract_jd(raw_jd)
│                                       # - map_evidence(profile, jd)
│                                       # - generate_resume(profile, jd, evidence_map)
│                                       # - validate_resume(resume)
└── validators.py                       # Resume validators
                                        # - validate_no_fabrication()
                                        # - validate_ats_formatting()
                                        # - validate_consistent_dates()
```

### Celery Workers (`backend/app/workers/`)
```
app/workers/
├── __init__.py                         # Exports celery_app and tasks
├── celery_app.py                       # Celery configuration
│                                       # - Redis broker
│                                       # - Result backend
│                                       # - Serialization settings
├── tasks.py                            # Celery tasks
│                                       # - generate_resume_task()
│                                       # - queue_application_task()
└── schedules.py                        # Beat schedule configuration
                                        # - Daily application queueing at 9 AM
```

### Utilities (`backend/app/utils/`)
```
app/utils/
├── __init__.py
├── text.py                             # Text processing utilities
│                                       # - extract_emails()
│                                       # - extract_urls()
│                                       # - clean_text()
│                                       # - highlight_keywords()
├── time.py                             # Time utilities
│                                       # - parse_date()
│                                       # - format_date()
│                                       # - get_date_range()
│                                       # - calculate_months_duration()
│                                       # - is_date_range_valid()
└── hashing.py                          # Hashing utilities
                                        # - hash_file_content()
                                        # - hash_string()
```

### Frontend (`backend/app/web/`)
```
app/web/
├── __init__.py
├── templates/
│   ├── layout.html                     # Base template
│   │                                   # - Navigation bar
│   │                                   # - Container layout
│   │                                   # - Footer
│   ├── profile.html                    # Profile editor
│   │                                   # - Personal info form
│   │                                   # - Education section
│   │                                   # - Experience section
│   │                                   # - Projects section
│   │                                   # - Skills section
│   ├── jobs.html                       # Job listing
│   │                                   # - Job cards
│   │                                   # - "Add Job" button
│   │                                   # - Filtering/search
│   ├── job_detail.html                 # Job details
│   │                                   # - Job info
│   │                                   # - Match analysis
│   │                                   # - "Generate Resume" button
│   ├── resume_preview.html             # Resume display
│   │                                   # - Summary, skills, experience
│   │                                   # - Projects, education
│   │                                   # - Validation status
│   │                                   # - Download button
│   └── applications.html               # Application log
                                        # - Application list
                                        # - Status filtering
                                        # - Details view
```

### Static Assets (`backend/app/web/static/`)
```
app/web/static/
└── styles.css                          # Comprehensive CSS styling (400+ lines)
                                        # - Root colors
                                        # - Responsive grid
                                        # - Form styling
                                        # - Button states
                                        # - Cards and badges
                                        # - Alerts and validation
                                        # - Dark mode variables
```

### Stubs for Expansion (`backend/app/`)
```
app/documents/
├── __init__.py                         # Package marker
└── [future: document processing logic]

app/notifications/
├── __init__.py                         # Package marker
└── [future: email/notification service]
```

## Testing (`backend/tests/`)
```
tests/
├── __init__.py
├── conftest.py                         # Pytest fixtures and configuration
│                                       # - test_db fixture
│                                       # - client fixture (TestClient)
├── test_jd_extraction.py               # JD extraction tests
│                                       # - test_jd_extract_schema()
│                                       # - test_jd_structure_validation()
├── test_resume_validation.py           # Resume validation tests
│                                       # - test_resume_fabrication_check()
│                                       # - test_ats_formatting_validation()
│                                       # - test_date_consistency()
└── test_matching.py                    # Match scoring tests
                                        # - test_match_score_calculation()
```

## Database Migrations (`backend/alembic/`)
```
alembic/
├── __init__.py
├── versions/
│   └── [auto-generated migration files]
├── script.py.mako                      # Migration template
├── env.py                              # Alembic environment configuration
└── alembic.ini                         # Alembic configuration file
```

## Scripts (`backend/scripts/`)
```
scripts/
├── seed.ps1                            # PowerShell seeding script
│                                       # - Creates demo user
│                                       # - Populates profile data
│                                       # - Creates sample job
└── seed_db.py                          # Python seeding script
                                        # - Programmatic database initialization
                                        # - Demo data creation
                                        # - Error handling
```

## Configuration Files
```
backend/
├── Makefile                            # Development commands
│                                       # - install, dev, test, lint, format
│                                       # - docker-build, docker-up, docker-down
├── pyproject.toml                      # Python project metadata
│                                       # - Dependencies (fastapi, sqlalchemy, etc.)
│                                       # - Dev dependencies (pytest, black, ruff)
│                                       # - Tool configurations
├── alembic.ini                         # Alembic migration configuration
├── .env.example                        # Environment variable template
│                                       # - All configurable settings
└── .gitignore                          # Git ignore patterns
```

## Root Configuration Files
```
autoapply-ats/
├── docker-compose.yml                  # Multi-container orchestration
│                                       # - PostgreSQL 16
│                                       # - Redis 7
│                                       # - FastAPI API
│                                       # - Celery Worker
│                                       # - Celery Beat
├── Dockerfile                          # Backend container image
│                                       # - Python 3.10-slim base
│                                       # - Dependencies installation
│                                       # - Health check
│                                       # - Uvicorn entry point
├── .env.example                        # Environment template (root)
├── .gitignore                          # Git ignore (root)
└── .github/workflows/                  # CI/CD pipelines
    └── tests.yml                       # GitHub Actions test workflow
```

## Documentation Files
```
docs/
├── api_complete.md                     # Complete API reference (600+ lines)
│                                       # - Endpoint documentation
│                                       # - Request/response examples
│                                       # - Error handling
│                                       # - Workflow examples
│                                       # - cURL command examples
├── architecture.md                     # System architecture
│                                       # - Component diagram
│                                       # - Data flow
│                                       # - Technology stack
└── ats_rules.md                        # ATS resume rules
                                        # - Formatting guidelines
                                        # - Keywords extraction
                                        # - Validation rules
```

## Root Documentation
```
autoapply-ats/
├── README.md                           # Main project guide (400+ lines)
│                                       # - Features overview
│                                       # - Quick start
│                                       # - Architecture explanation
│                                       # - Workflow example
│                                       # - Compliance notes
│                                       # - Roadmap
├── QUICK_REFERENCE.md                  # Command reference card
│                                       # - Start/stop commands
│                                       # - API examples
│                                       # - Port reference
│                                       # - Troubleshooting
├── WINDOWS_SETUP.md                    # Windows-specific guide (800+ lines)
│                                       # - Prerequisites
│                                       # - Step-by-step setup
│                                       # - Troubleshooting
│                                       # - VS Code configuration
│                                       # - Docker commands
├── DEPLOYMENT_CHECKLIST.md             # Pre-deployment checklist
│                                       # - Feature verification
│                                       # - Testing checklist
│                                       # - Deployment steps
└── MVP_COMPLETE.md                     # MVP status document
                                        # - Detailed feature list
                                        # - Code statistics
                                        # - Ready-to-deploy status
```

## Summary Statistics

| Category | Count | Details |
|----------|-------|---------|
| **Models** | 11 | User, Profile, Job, Resume, Application, etc. |
| **Schemas** | 19 | Pydantic V2 validation classes |
| **Services** | 8 | Auth, Profile, Job, Resume, Matching, Document, Audit, Application |
| **API Routes** | 5 | Auth, Profile, Jobs, Resumes, Applications |
| **API Endpoints** | 15+ | GET, POST, PUT operations |
| **Tests** | 10+ | Unit tests for core logic |
| **Templates** | 6 | HTML server-rendered views |
| **Utilities** | 3 | Text, Time, Hashing helpers |
| **Configuration** | 4+ | .env, pyproject.toml, alembic.ini, docker-compose.yml |
| **Documentation** | 7 | README, QUICK_REFERENCE, WINDOWS_SETUP, etc. |
| **Total Files** | 100+ | Complete MVP codebase |

## Quick Navigation

### For Developers
- Start here: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- Commands: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- API: [docs/api_complete.md](docs/api_complete.md)
- Code: `backend/app/`

### For Operations
- Docker: [docker-compose.yml](docker-compose.yml)
- Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- Status: [MVP_COMPLETE.md](MVP_COMPLETE.md)

### For Product
- Features: [README.md](README.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Roadmap: See README.md "Roadmap"

---

**Last Updated**: 2024
**Project Status**: MVP Complete ✅
**Version**: 0.1.0
