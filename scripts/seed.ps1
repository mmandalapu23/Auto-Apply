# PowerShell script to seed initial data
Write-Host "Seeding database..." -ForegroundColor Green

$backendPath = Join-Path (Get-Location) "backend"
Set-Location $backendPath

# Run seed script
python << 'EOF'
import sys
import json
from datetime import datetime
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import User, Profile, Experience, Project, Education, Skill, Job
from app.core.security import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Check if seed data already exists
existing_user = db.query(User).filter(User.email == "demo@autoapply.ai").first()
if existing_user:
    print("✓ Database already seeded")
    db.close()
    sys.exit(0)

try:
    # Create demo user
    demo_user = User(
        email="demo@autoapply.ai",
        hashed_password=hash_password("password123"),
        full_name="John Doe",
        is_active=True
    )
    db.add(demo_user)
    db.flush()  # Get ID without committing
    
    print(f"✓ Created user: {demo_user.email}")
    
    # Create profile
    profile = Profile(
        user_id=demo_user.id,
        email="john.doe@email.com",
        phone="+1-555-0100",
        location="San Francisco, CA",
        summary="Full-stack software engineer with 6+ years of experience building scalable web applications and APIs.",
        degree="Bachelor of Science",
        university="UC Berkeley",
        graduation_year=2018
    )
    db.add(profile)
    db.flush()
    
    print(f"✓ Created profile for {demo_user.full_name}")
    
    # Add experience
    exp1_bullets = json.dumps([
        {"text": "Led development of microservices architecture serving 10M+ daily users", "tech": ["Python", "FastAPI", "PostgreSQL"]},
        {"text": "Optimized database queries reducing latency by 40%", "tech": ["PostgreSQL", "Redis"]},
        {"text": "Mentored team of 3 junior engineers", "tech": ["Python"]},
        {"text": "Implemented CI/CD pipeline using Docker and Kubernetes", "tech": ["Docker", "Kubernetes", "GitHub Actions"]}
    ])
    
    exp1 = Experience(
        profile_id=profile.id,
        company="TechCorp",
        title="Senior Backend Engineer",
        start_date="2021-06",
        end_date="2024-01",
        is_current=False,
        description=exp1_bullets
    )
    db.add(exp1)
    
    exp2_bullets = json.dumps([
        {"text": "Built REST APIs for mobile app serving 500K daily users", "tech": ["Python", "Django", "PostgreSQL"]},
        {"text": "Implemented user authentication and authorization system", "tech": ["JWT", "OAuth2"]},
        {"text": "Created monitoring and logging infrastructure", "tech": ["ELK Stack", "Datadog"]}
    ])
    
    exp2 = Experience(
        profile_id=profile.id,
        company="StartupXYZ",
        title="Backend Engineer",
        start_date="2019-03",
        end_date="2021-05",
        is_current=False,
        description=exp2_bullets
    )
    db.add(exp2)
    
    print("✓ Added 2 work experiences")
    
    # Add projects
    proj1_bullets = json.dumps([
        {"text": "Built real-time chat application with WebSocket support", "tech": ["Python", "FastAPI", "WebSocket", "Redis"]},
        {"text": "Created admin dashboard for system monitoring", "tech": ["React", "D3.js"]},
        {"text": "Deployed to AWS ECS with auto-scaling", "tech": ["AWS", "Docker", "Kubernetes"]}
    ])
    
    proj1 = Project(
        profile_id=profile.id,
        name="Real-time Chat Platform",
        description=proj1_bullets,
        url="https://github.com/johndoe/chat-platform"
    )
    db.add(proj1)
    
    proj2_bullets = json.dumps([
        {"text": "Open-source Python library for data validation", "tech": ["Python", "Pydantic"]},
        {"text": "10K+ GitHub stars, used in production by 50+ companies", "tech": []},
        {"text": "Maintained for 3 years with active community", "tech": []}
    ])
    
    proj2 = Project(
        profile_id=profile.id,
        name="DataValidator Python Library",
        description=proj2_bullets,
        url="https://github.com/johndoe/datavalidator"
    )
    db.add(proj2)
    
    print("✓ Added 2 projects")
    
    # Add education
    edu1 = Education(
        profile_id=profile.id,
        institution="UC Berkeley",
        degree="Bachelor of Science",
        field="Computer Science",
        start_date="2014-09",
        end_date="2018-05",
        gpa="3.8"
    )
    db.add(edu1)
    
    edu2 = Education(
        profile_id=profile.id,
        institution="Coursera",
        degree="Certificate",
        field="Machine Learning Specialization",
        start_date="2021-01",
        end_date="2021-06",
        gpa=None
    )
    db.add(edu2)
    
    print("✓ Added 2 education entries")
    
    # Add skills
    skills_data = [
        ("Python", "Language", "Expert"),
        ("JavaScript", "Language", "Advanced"),
        ("FastAPI", "Framework", "Expert"),
        ("Django", "Framework", "Advanced"),
        ("PostgreSQL", "Database", "Expert"),
        ("MongoDB", "Database", "Intermediate"),
        ("Docker", "DevOps", "Advanced"),
        ("Kubernetes", "DevOps", "Intermediate"),
        ("AWS", "Cloud", "Advanced"),
        ("Redis", "Cache", "Advanced"),
        ("Git", "Tool", "Expert"),
        ("React", "Frontend", "Intermediate"),
        ("REST APIs", "Architecture", "Expert"),
        ("Microservices", "Architecture", "Advanced"),
        ("SQL", "Database", "Expert"),
    ]
    
    for skill_name, category, proficiency in skills_data:
        skill = Skill(
            profile_id=profile.id,
            name=skill_name,
            category=category,
            proficiency=proficiency
        )
        db.add(skill)
    
    print(f"✓ Added {len(skills_data)} skills")
    
    # Add sample job posting
    sample_jd = """Senior Python Backend Engineer

About the Role:
We're looking for an experienced backend engineer to join our growing platform team. You'll work on building and scaling our core services that power our product for millions of users worldwide.

Responsibilities:
- Design and implement scalable microservices using Python
- Optimize database queries and system architecture
- Lead code reviews and mentor junior engineers
- Collaborate with product and infrastructure teams
- Implement monitoring and observability systems

Required Skills:
- 5+ years of experience with Python
- Strong understanding of relational databases (PostgreSQL or MySQL)
- Experience with REST APIs and microservices architecture
- Proficiency with Docker and container orchestration
- Experience with cloud platforms (AWS, GCP, or Azure)
- Strong communication and leadership skills

Nice to Have:
- Experience with FastAPI or Starlette
- Kubernetes experience
- Experience with message queues (RabbitMQ, Kafka)
- Open source contributions
- ML/Data engineering background

Compensation:
- $180K - $220K base salary
- Equity
- Full benefits package
- Remote-friendly

Location: San Francisco, CA (Hybrid)"""
    
    job = Job(
        user_id=demo_user.id,
        title="Senior Python Backend Engineer",
        company="TechCorp",
        url="https://techcorp.com/careers/senior-backend-engineer",
        raw_jd=sample_jd
    )
    db.add(job)
    
    print("✓ Added sample job posting")
    
    # Commit all data
    db.commit()
    
    print("\n✅ Database seeding completed successfully!")
    print(f"Demo user email: demo@autoapply.ai")
    print(f"Demo password: password123")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error seeding database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()

EOF

Write-Host "Seeding complete!" -ForegroundColor Green

