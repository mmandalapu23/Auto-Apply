# AutoApply ATS - Setup Summary

## Overview

This document summarizes the setup and configuration work done to get the AutoApply ATS application running locally.

---

## 1. Environment Setup

### Problem: Docker Desktop Not Running
- Initial attempt to use Docker failed
- **Solution**: Switched to local Python virtual environment

### Problem: SSL Certificate Issues
- `pip install` commands failed due to `SSL_CERT_FILE` environment variable pointing to a PostgreSQL CA bundle
- **Solution**: Clear SSL environment variables before each command:
  ```powershell
  $env:SSL_CERT_FILE=""; $env:CURL_CA_BUNDLE=""; $env:REQUESTS_CA_BUNDLE=""
  ```

### Virtual Environment Created
```powershell
cd c:\Users\Mahesh\projects\JobApply\autoapply-ats\backend
python -m venv venv
.\venv\Scripts\activate
```

---

## 2. Dependency Installation Fixes

### Problem: Hatchling Build Error
- Error: "Unable to determine which files to ship in wheel"
- **Solution**: Added wheel target configuration to `pyproject.toml`:
  ```toml
  [tool.hatch.build.targets.wheel]
  packages = ["app"]
  ```

### Problem: Invalid `testclient` Dependency
- Error: Package `testclient` doesn't exist
- **Solution**: Removed from dev dependencies (it's part of `starlette`)

### Successful Installation
```powershell
$env:SSL_CERT_FILE=""; pip install -e ".[dev]"
```

---

## 3. Code Fixes

### Fix 1: HTTPAuthCredentials Import Error
- **File**: `app/api/deps.py`
- **Problem**: `HTTPAuthCredentials` doesn't exist
- **Solution**: Changed to `HTTPAuthorizationCredentials`

### Fix 2: SQLAlchemy Reserved Attribute
- **File**: `app/db/models/audit.py`
- **Problem**: `metadata` is a reserved SQLAlchemy attribute
- **Solution**: Renamed attribute to `context` while keeping column name as "metadata":
  ```python
  context = Column("metadata", Text, nullable=True)
  ```

### Fix 3: Missing ApplicationStatus Export
- **File**: `app/db/models/__init__.py`
- **Problem**: `ApplicationStatus` not exported
- **Solution**: Added to `__all__` exports

### Fix 4: bcrypt/passlib Compatibility
- **File**: `app/core/security.py`
- **Problem**: passlib 1.7.4 incompatible with bcrypt 5.0.0
- **Solution**: Replaced passlib with direct bcrypt usage:
  ```python
  import bcrypt
  
  def hash_password(password: str) -> str:
      return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
  
  def verify_password(plain_password: str, hashed_password: str) -> bool:
      return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
  ```

---

## 4. Database Configuration

### Switched from PostgreSQL to SQLite
- **File**: `app/core/config.py`
- **Change**: 
  ```python
  # Before
  DATABASE_URL: str = "postgresql://user:password@localhost:5432/autoapply"
  
  # After
  DATABASE_URL: str = "sqlite:///./autoapply.db"
  ```

### Database Seeding
- **Script**: `scripts/seed_db.py`
- Fixed model field mismatches to match actual schema
- Creates demo user and sample data:
  - Email: `demo@autoapply.ai`
  - Password: `password123`

---

## 5. New Features Added

### Greenhouse Job Import
- **File**: `app/services/job_source_service.py`
- Fetches jobs from Greenhouse API
- Filters by keywords (Data Engineer, Data Analyst, Software Engineer, etc.)
- Strips HTML from job descriptions

### Job Import Script
- **File**: `scripts/import_jobs.py`
- Imports real jobs from company Greenhouse boards:
  - Airbnb, Discord, Stripe, Figma, Coinbase
  - Squarespace, Lyft, Benchling, Chime, Airtable
  - And more...

### Storage Abstraction
- **File**: `app/services/storage_service.py`
- `LocalStorageAdapter` - stores files locally
- `S3StorageAdapter` - stores files in S3/R2
- Configurable via `STORAGE_BACKEND` setting

### Frontend Web Routes
- **File**: `app/web/router.py`
- `GET /` - Redirects to /jobs
- `GET /jobs` - Lists all jobs
- `GET /jobs/{id}` - Job detail page

### Frontend Config API
- **File**: `app/api/routers/frontend.py`
- `GET /frontend/config` - Returns frontend configuration

---

## 6. Running the Application

### Start Server
```powershell
cd c:\Users\Mahesh\projects\JobApply\autoapply-ats\backend
$env:SSL_CERT_FILE=""; $env:CURL_CA_BUNDLE=""; $env:REQUESTS_CA_BUNDLE=""
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8001
```

### Access Points
| URL | Description |
|-----|-------------|
| http://localhost:8001/jobs | Job listings (Frontend) |
| http://localhost:8001/docs | API Documentation (Swagger) |
| http://localhost:8001/health | Health check |

### Import Fresh Jobs
```powershell
cd c:\Users\Mahesh\projects\JobApply\autoapply-ats\backend
$env:SSL_CERT_FILE=""
.\venv\Scripts\python.exe scripts\import_jobs.py
```

---

## 7. Current State

### Working Features
- ✅ FastAPI server running on port 8001
- ✅ SQLite database with demo data
- ✅ Job listings page with real jobs from Greenhouse
- ✅ API documentation at /docs
- ✅ Health check endpoint
- ✅ Job import from external sources

### Jobs Imported (15 total)
| Company | Role |
|---------|------|
| Airbnb | Business Data Analyst (12 Month FTC) |
| Discord | Data Engineering Manager |
| Discord | Data Scientist, Analytics - Ads Reporting |
| Coinbase | AI Growth Lead (Staff Software Engineer) |
| Squarespace | Data Analyst, Performance & Strategic Analytics |
| Squarespace | Engineering Team Manager, Website Fundamentals (Backend) |
| Squarespace | Founding Machine Learning Engineer, Domains Search |
| Squarespace | Founding Senior Data Engineer, Domains Search |
| Lyft | Backend Software Engineer |
| Benchling | Full Stack, Application Platform (High Seniority) |
| Chime | Backend Engineer |
| Chime | Data Analyst, Lending |
| Airtable | Data Engineer |
| Airtable | Data Scientist, GTM Analytics |
| Airtable | Data Scientist, Product Analytics |

---

## 8. Files Modified/Created

### Modified Files
- `app/core/config.py` - SQLite database URL
- `app/core/security.py` - bcrypt password hashing
- `app/api/deps.py` - Fixed import
- `app/db/models/audit.py` - Renamed metadata attribute
- `app/db/models/__init__.py` - Added exports
- `app/main.py` - Mounted static files, added web router
- `app/services/audit_service.py` - Updated to use `context` parameter
- `pyproject.toml` - Fixed build configuration
- `scripts/seed_db.py` - Fixed model fields

### New Files Created
- `app/services/job_source_service.py` - Greenhouse integration
- `app/services/storage_service.py` - Storage abstraction
- `app/api/routers/frontend.py` - Frontend config endpoint
- `app/web/router.py` - Web page routes
- `scripts/import_jobs.py` - Job import script
- `docs/SETUP_SUMMARY.md` - This documentation

---

## 9. Next Steps (TODO)

- [ ] Wire up user authentication to web routes
- [ ] Add job application tracking
- [ ] Implement resume generation with LLM
- [ ] Add more job sources (LinkedIn, Indeed via scraping)
- [ ] Set up Celery for background job imports
- [ ] Deploy to production with PostgreSQL
