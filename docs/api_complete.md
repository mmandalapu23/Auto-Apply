# AutoApply ATS - Complete API Guide

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT Bearer token in header:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Authentication

#### Register New User
```
POST /auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "john@example.com"
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "john@example.com"
}
```

### Profile Management

#### Get User Profile
```
GET /profile
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "location": "San Francisco, CA",
  "summary": "Experienced backend engineer...",
  "degree": "Bachelor of Science",
  "university": "UC Berkeley",
  "graduation_year": 2018,
  "experiences": [
    {
      "id": 1,
      "company": "TechCorp",
      "title": "Senior Backend Engineer",
      "start_date": "2021-06",
      "end_date": "2024-01",
      "is_current": false,
      "bullets": [
        {
          "text": "Led development of microservices",
          "tech": ["Python", "FastAPI"]
        }
      ]
    }
  ],
  "projects": [...],
  "educations": [...],
  "skills": [...],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

#### Update Profile
```
PUT /profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "location": "San Francisco, CA",
  "summary": "Backend engineer with 6+ years experience",
  "degree": "Bachelor of Science",
  "university": "UC Berkeley",
  "graduation_year": 2018,
  "experiences": [
    {
      "company": "TechCorp",
      "title": "Senior Backend Engineer",
      "start_date": "2021-06",
      "end_date": "2024-01",
      "is_current": false,
      "bullets": [
        {
          "text": "Led development of microservices architecture",
          "tech": ["Python", "FastAPI", "PostgreSQL"]
        }
      ]
    }
  ],
  "projects": [
    {
      "name": "Chat Platform",
      "bullets": [
        {
          "text": "Built real-time chat with WebSocket support",
          "tech": ["Python", "FastAPI", "WebSocket"]
        }
      ],
      "url": "https://github.com/user/chat-platform"
    }
  ],
  "educations": [
    {
      "institution": "UC Berkeley",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "start_date": "2014-09",
      "end_date": "2018-05",
      "gpa": "3.8"
    }
  ],
  "skills": [
    {
      "name": "Python",
      "category": "Language",
      "proficiency": "Expert"
    },
    {
      "name": "FastAPI",
      "category": "Framework",
      "proficiency": "Expert"
    }
  ]
}

Response: 200 OK
(Returns updated profile)
```

### Job Management

#### Create Job Posting
```
POST /jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Python Backend Engineer",
  "company": "TechCorp",
  "url": "https://techcorp.com/careers/...",
  "raw_jd": "Senior Python Backend Engineer\n\nResponsibilities:\n- Build scalable APIs\n- Design database schemas\n..."
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "title": "Senior Python Backend Engineer",
  "company": "TechCorp",
  "url": "https://techcorp.com/careers/...",
  "raw_jd": "...",
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

#### List Jobs
```
GET /jobs?skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "title": "Senior Python Backend Engineer",
    "company": "TechCorp",
    ...
  }
]
```

#### Get Job Details
```
GET /jobs/{job_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "title": "Senior Python Backend Engineer",
  "company": "TechCorp",
  "raw_jd": "...",
  "extracted_data": {
    "responsibilities": [
      {
        "text": "Build scalable microservices",
        "required": true
      }
    ],
    "must_have_skills": ["Python", "FastAPI", "PostgreSQL"],
    "nice_to_have_skills": ["Docker", "Kubernetes"],
    "keywords": ["backend", "api", "microservices"],
    "seniority_signals": ["Senior"],
    "years_experience": 5
  },
  "created_at": "2024-01-15T10:00:00"
}
```

#### Extract JD Structure
```
POST /jobs/{job_id}/extract
Authorization: Bearer <token>

Response: 200 OK
{
  "responsibilities": [
    {
      "text": "Build scalable microservices architecture",
      "required": true
    }
  ],
  "must_have_skills": ["Python", "FastAPI", "PostgreSQL"],
  "nice_to_have_skills": ["Docker", "Kubernetes"],
  "keywords": ["backend", "api", "microservices"],
  "seniority_signals": ["Senior"],
  "years_experience": 5
}
```

#### Match Job to Profile
```
POST /jobs/{job_id}/match
Authorization: Bearer <token>

Response: 200 OK
{
  "job_id": 1,
  "match_score": {
    "overall_score": 0.85,
    "skills_match": 0.9,
    "experience_match": 0.8,
    "seniority_match": 0.7,
    "missing_requirements": [
      {
        "type": "skill",
        "name": "Kubernetes",
        "importance": "nice_to_have"
      }
    ],
    "matched_keywords": ["Python", "FastAPI", "backend"],
    "unmatched_keywords": ["Kubernetes", "Go"]
  },
  "evidence_map": {
    "matched_items": {
      "must_have_skills": [
        {
          "type": "skill",
          "id": 1,
          "text": "Python"
        }
      ],
      "experience": [...]
    },
    "missing_items": [...]
  }
}
```

### Resume Generation

#### Generate Resume
```
POST /resumes
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_id": 1
}

Response: 200 OK
{
  "resume_id": 1,
  "structured_data": {
    "summary": {
      "text": "Senior backend engineer with 6+ years experience...",
      "evidence_refs": []
    },
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience": [
      {
        "company": "TechCorp",
        "title": "Senior Backend Engineer",
        "start_date": "06/2021",
        "end_date": "01/2024",
        "bullets": [
          {
            "text": "Led development of microservices architecture serving 10M+ users",
            "evidence_refs": [
              {
                "type": "experience",
                "id": 1,
                "bullet_idx": 0,
                "text": "Led development of microservices architecture serving 10M+ daily users"
              }
            ]
          }
        ]
      }
    ],
    "projects": [...],
    "education": [...]
  },
  "ats_text": "SENIOR BACKEND ENGINEER\n...",
  "validation": {
    "passed": true,
    "issues": []
  },
  "pdf_path": "resumes/resume_1.html"
}
```

#### Get Resume
```
GET /resumes/{resume_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "job_id": 1,
  "structured_data": {...},
  "ats_text": "...",
  "validation_passed": {
    "passed": true,
    "issues": []
  },
  "pdf_path": "resumes/resume_1.html",
  "created_at": "2024-01-15T10:00:00"
}
```

#### Get Resume PDF
```
GET /resumes/{resume_id}/pdf
Authorization: Bearer <token>

Response: 200 OK
{
  "pdf_path": "resumes/resume_1.html"
}
```

### Applications

#### Create Application
```
POST /applications
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_id": 1
}

Response: 201 Created
{
  "id": 1,
  "job_id": 1,
  "status": "ready_for_review",
  "created_at": "2024-01-15T10:00:00"
}
```

#### List Applications
```
GET /applications?status=ready_for_review&skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "job_id": 1,
    "resume_id": 1,
    "status": "ready_for_review",
    "match_score": {...},
    "missing_requirements": [...],
    "created_at": "2024-01-15T10:00:00"
  }
]
```

#### Get Application
```
GET /applications/{app_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "job_id": 1,
  "resume_id": 1,
  "status": "ready_for_review",
  "match_score": {
    "overall_score": 0.85,
    ...
  },
  "missing_requirements": [...],
  "created_at": "2024-01-15T10:00:00"
}
```

#### Update Application Status
```
PUT /applications/{app_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "submitted"
}

Response: 200 OK
{
  "id": 1,
  "status": "submitted",
  "updated_at": "2024-01-15T10:05:00"
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 404 | Not Found - Resource not found |
| 500 | Server Error |

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Example Workflow

1. **Register User**
   ```
   POST /auth/register
   ```

2. **Update Profile**
   ```
   PUT /profile
   ```

3. **Create Job**
   ```
   POST /jobs
   ```

4. **Match Job to Profile**
   ```
   POST /jobs/{job_id}/match
   ```

5. **Generate Resume**
   ```
   POST /resumes
   ```

6. **Create Application**
   ```
   POST /applications
   ```

7. **List Applications**
   ```
   GET /applications
   ```

## Testing with cURL (Windows PowerShell)

```powershell
# Register
$token = Invoke-WebRequest -Uri http://localhost:8000/api/v1/auth/register `
  -Method POST `
  -ContentType application/json `
  -Body '{"email":"test@example.com","password":"password123","full_name":"John Doe"}' | ConvertFrom-Json

$token = $token.access_token

# Get Profile
Invoke-WebRequest -Uri http://localhost:8000/api/v1/profile `
  -Headers @{ Authorization = "Bearer $token" }

# Create Job
Invoke-WebRequest -Uri http://localhost:8000/api/v1/jobs `
  -Method POST `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType application/json `
  -Body '{"title":"Senior Developer","company":"TechCorp","raw_jd":"..."}'
```

## Interactive Testing

Use Swagger UI for interactive testing:
- **URL**: http://localhost:8000/docs
- Provides request/response preview
- Auto-generates curl commands
- Test all endpoints easily

## Rate Limiting

Current MVP has no rate limiting. For production, implement:
- Per-user rate limits
- IP-based rate limiting
- Sliding window rate limiting

## Pagination

For list endpoints, use `skip` and `limit`:
```
GET /jobs?skip=0&limit=50
GET /jobs?skip=50&limit=50
```

## Search (Future)

Planned for v0.2:
- Search jobs by company, title
- Filter applications by status, date range
- Full-text search on JD content
