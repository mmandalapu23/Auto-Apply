# AutoApply ATS - Getting Started Guide

## 🎯 Welcome to AutoApply ATS!

This is your complete AI-powered job application system. This guide will help you get up and running in minutes.

## ⚡ Quick Start (5 minutes)

### Step 1: Prerequisites
- Python 3.10+ installed
- Docker Desktop installed (recommended)
- Git installed
- VS Code (optional but recommended)

### Step 2: Start the Application

#### Option A: Docker (Easiest - All-in-one)
```powershell
# Navigate to project
cd c:\Users\Mahesh\projects\JobApply\autoapply-ats

# Start all services
docker-compose up -d

# Wait 10 seconds for services to initialize
Start-Sleep -Seconds 10

# Verify all services are running
docker-compose ps

# Access the application
Start-Process "http://localhost:8000/docs"
```

#### Option B: Local Python (More Control)
```powershell
cd c:\Users\Mahesh\projects\JobApply\autoapply-ats\backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[dev]"

# Setup database
alembic upgrade head
python scripts\seed_db.py

# Start server
uvicorn app.main:app --reload
```

### Step 3: Log In
1. Open http://localhost:8000/docs
2. Use demo credentials:
   - **Email**: demo@autoapply.ai
   - **Password**: password123
3. Click "Authorize" button
4. Enter credentials and authorize

### Step 4: You're Ready!
- ✅ Profile is pre-filled with demo data
- ✅ Sample job is available
- ✅ You can generate a resume immediately

## 📖 Understanding the System

### Core Concepts (2 minutes)

**AutoApply ATS** helps you automatically generate tailored resumes for job applications. Here's how it works:

1. **Profile** - Your background (education, experience, projects, skills)
2. **Job** - A job posting you find
3. **Extract** - System parses the job description
4. **Match** - Calculates how well your profile matches the job
5. **Generate** - Creates a tailored resume with evidence from your profile
6. **Track** - Logs all applications and their status

### Key Features

- ✨ **Evidence-Based** - Every resume claim is grounded in your actual profile
- 🔒 **No Fabrication** - System won't make up experience or skills
- 📊 **Match Scoring** - See how well you fit each job
- 📄 **Multiple Formats** - ATS-optimized text, HTML, PDF
- 📋 **Application Tracking** - Keep history of all applications
- 🔄 **Auto-Scheduling** - Queue applications for daily review

## 🚀 First Workflow (10 minutes)

### 1. Review Your Profile
```
API: GET /api/v1/profile
UI: http://localhost:8000/ (Profile section)
```
- Check your experiences, projects, education, skills
- Add/edit as needed

### 2. Add a Job
```
API: POST /api/v1/jobs
UI: http://localhost:8000/ (Jobs section)
Body:
{
  "title": "Senior Python Engineer",
  "company": "MyCompany",
  "url": "https://example.com/job",
  "raw_jd": "Paste the job description text here..."
}
```

### 3. Extract Job Requirements
```
API: POST /api/v1/jobs/{job_id}/extract
```
System analyzes the job description to extract:
- Must-have skills
- Nice-to-have skills
- Required experience level
- Keywords

### 4. Check Match Score
```
API: POST /api/v1/jobs/{job_id}/match
```
Get:
- Overall match score (0-100%)
- Skill match breakdown
- Missing requirements list

### 5. Generate Resume
```
API: POST /api/v1/resumes
Body:
{
  "job_id": 1
}
```
System creates a resume with:
- All information tied to your profile
- ATS-friendly formatting
- Evidence references for every claim
- Highlighted job-matching skills

### 6. Review & Apply
```
API: GET /api/v1/resumes/{resume_id}
```
- Review the generated resume
- Check validation status
- Download if approved
- Track application status

## 🔗 API Reference

### Quick API Calls (PowerShell Examples)

#### Login
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"demo@autoapply.ai","password":"password123"}'

$token = ($response.Content | ConvertFrom-Json).access_token
$headers = @{"Authorization" = "Bearer $token"}
```

#### Get Profile
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile" `
  -Headers $headers | ConvertFrom-Json
```

#### Create Job
```powershell
$jobData = @{
  title = "Senior Backend Engineer"
  company = "TechCorp"
  url = "https://example.com/job"
  raw_jd = "Job description here..."
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/jobs" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $jobData
```

#### Generate Resume
```powershell
$resumeData = @{job_id = 1} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/resumes" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $resumeData
```

For more APIs, see [docs/api_complete.md](docs/api_complete.md)

## 📚 Learning Resources

### Understanding Each Component

1. **Profile Management**
   - File: `backend/app/services/profile_service.py`
   - Manages education, experience, projects, skills
   - Docs: See profile.html template

2. **Job Processing**
   - File: `backend/app/services/job_service.py`
   - Stores job postings and extracted data
   - LLM extraction: `backend/app/llm/client.py`

3. **Resume Generation**
   - File: `backend/app/services/resume_service.py`
   - 4-step pipeline in `backend/app/llm/pipeline.py`
   - Validates evidence grounding

4. **Match Scoring**
   - File: `backend/app/services/matching_service.py`
   - Compares profile to JD requirements
   - Calculates skill and experience match

5. **Application Tracking**
   - File: `backend/app/services/application_service.py`
   - Tracks application status and history
   - Audit logging in `audit_service.py`

### Advanced Topics

- **Evidence Grounding** - See [README.md](README.md#evidence-grounding)
- **ATS Formatting** - See [docs/ats_rules.md](docs/ats_rules.md)
- **Architecture** - See [docs/architecture.md](docs/architecture.md)
- **API Details** - See [docs/api_complete.md](docs/api_complete.md)

## 🛠️ Common Tasks

### Add a Skill
```powershell
# Update profile with new skill
$profileData = @{
  skills = @(
    @{name = "Python"; category = "Backend"; proficiency_level = 5},
    @{name = "FastAPI"; category = "Backend"; proficiency_level = 5},
    @{name = "React"; category = "Frontend"; proficiency_level = 3}
  )
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile" `
  -Method PUT `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $profileData
```

### Update Experience
```powershell
# Modify existing experience
# Update via PUT /profile with full profile data
```

### View Application History
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/applications" `
  -Headers $headers | ConvertFrom-Json
```

### Change Application Status
```powershell
$statusData = @{
  status = "SUBMITTED"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/applications/{app_id}" `
  -Method PUT `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $statusData
```

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Database Connection Failed
```powershell
# Check Docker containers
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Recreate database
docker-compose down -v
docker-compose up -d
```

### ModuleNotFoundError
```powershell
# Make sure you're in virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -e ".[dev]"
```

### Token Expired
```powershell
# Get new token by logging in again
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"demo@autoapply.ai","password":"password123"}'
```

For more issues, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md#common-issues--solutions)

## 📞 Support

### Getting Help
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
2. Review [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for setup issues
3. See [docs/api_complete.md](docs/api_complete.md) for API details
4. Check [README.md](README.md) for architecture/concepts

### Documentation Files
- **README.md** - Project overview and architecture
- **QUICK_REFERENCE.md** - Commands and API examples
- **WINDOWS_SETUP.md** - Detailed Windows setup guide
- **docs/api_complete.md** - Full API documentation
- **docs/architecture.md** - System architecture
- **docs/ats_rules.md** - Resume formatting rules

## 🎓 Learning Path

### Day 1: Setup & Basics (30 minutes)
1. Complete Quick Start above
2. Review [README.md](README.md#core-concepts)
3. Test API with demo data
4. Generate first resume

### Day 2: Integration (1 hour)
1. Add your own profile data
2. Find and add a real job posting
3. Generate resume for that job
4. Review match score and missing requirements

### Day 3: Customization (depends)
1. Integrate real LLM (OpenAI/Anthropic) - see [backend/app/llm/client.py](backend/app/llm/client.py)
2. Implement PDF rendering - see [backend/app/services/document_service.py](backend/app/services/document_service.py)
3. Deploy to production - see [WINDOWS_SETUP.md#production](WINDOWS_SETUP.md)

## 🚀 Next Steps

### Immediate (Today)
- [x] Get system running
- [x] Test with demo data
- [x] Generate a test resume
- [x] Explore the API documentation

### Short-term (This week)
- [ ] Add your own profile data
- [ ] Test with real job postings
- [ ] Review generated resumes
- [ ] Integrate real LLM for better extraction

### Medium-term (Next month)
- [ ] Deploy to cloud (AWS/GCP)
- [ ] Build React frontend (optional)
- [ ] Integrate job boards (LinkedIn/Indeed)
- [ ] Add advanced matching rules

### Long-term (Next quarter)
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] Bulk job import
- [ ] Mobile app

## ✅ Checklist

- [ ] Docker installed and running
- [ ] Application started (`docker-compose up -d` or `uvicorn`)
- [ ] API accessible at http://localhost:8000/docs
- [ ] Logged in with demo@autoapply.ai
- [ ] Profile visible with demo data
- [ ] Sample job available
- [ ] First resume generated successfully
- [ ] All checks passed ✅

**You're ready to start using AutoApply ATS!** 🎉

---

**Need help?** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or check documentation in `/docs`

**Want to contribute?** See [README.md](README.md#code-quality) for development guidelines

**Ready to deploy?** Follow [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for production setup
