# API Reference

Base URL: `http://localhost:8000/api/v1`

## Authentication

- JWT Bearer tokens in `Authorization: Bearer <token>` header
- Tokens expire after 30 minutes (configurable)

## Endpoints

### Health Check
```
GET /health
```
Returns API status.

### Auth
- `POST /auth/register` - Create new user
- `POST /auth/login` - Get access token

### Profiles
- `GET /profiles/me` - Get current user profile
- `PUT /profiles/me` - Update profile
- `POST /profiles/resumes` - Upload resume

### Jobs
- `GET /jobs` - List jobs
- `POST /jobs` - Create job listing
- `GET /jobs/{job_id}` - Get job details

### Applications
- `GET /applications` - List applications
- `POST /applications` - Create application
- `GET /applications/{app_id}/status` - Check status

### Matching
- `POST /matching/score` - Score candidate-job fit
- `POST /matching/extract-jd` - Extract JD elements

[TODO: Add detailed endpoint specifications with request/response bodies]
