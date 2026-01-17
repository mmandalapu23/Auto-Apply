"""Seed database with demo data (Python version)."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.db.models import (
    User, Profile, Experience, Project, Education, Skill, Job
)
from app.db.session import SessionLocal, engine
from app.core.security import hash_password
from sqlalchemy import text
from datetime import datetime

# Create all tables
def init_db():
    """Initialize database."""
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)


def seed_db():
    """Seed database with demo data."""
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing_user = db.query(User).filter(User.email == "demo@autoapply.ai").first()
        if existing_user:
            print("✓ Database already seeded")
            return
        
        # Create user
        user = User(
            email="demo@autoapply.ai",
            hashed_password=hash_password("password123"),
            full_name="Demo User",
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            email="demo@autoapply.ai",
            phone="+1-555-0123",
            location="San Francisco, CA",
            summary="Full-stack engineer with 5+ years experience in Python, JavaScript, and cloud infrastructure.",
            degree="BS Computer Science",
            university="UC Berkeley",
            graduation_year=2018
        )
        db.add(profile)
        db.flush()
        
        # Add experiences
        exp1 = Experience(
            profile_id=profile.id,
            title="Senior Backend Engineer",
            company="TechCorp",
            start_date="2021-01",
            end_date=None,
            is_current=True,
            description="Led backend services team building microservices with Python, FastAPI, PostgreSQL, Redis, and Docker"
        )
        exp2 = Experience(
            profile_id=profile.id,
            title="Software Engineer",
            company="StartupXYZ",
            start_date="2019-03",
            end_date="2020-12",
            is_current=False,
            description="Built microservices using Python, JavaScript, React, and AWS"
        )
        db.add_all([exp1, exp2])
        db.flush()
        
        # Add projects
        proj1 = Project(
            profile_id=profile.id,
            name="Real-time Chat Platform",
            description="WebSocket-based chat with 10k+ concurrent users using Python, FastAPI, WebSocket, and PostgreSQL",
            url="https://github.com/demo/chat-platform"
        )
        proj2 = Project(
            profile_id=profile.id,
            name="Data Validator Library",
            description="Open-source validation library with 5k+ GitHub stars built with Python and Pydantic",
            url="https://github.com/demo/data-validator"
        )
        db.add_all([proj1, proj2])
        db.flush()
        
        # Add education
        edu1 = Education(
            profile_id=profile.id,
            institution="UC Berkeley",
            degree="Bachelor of Science",
            field="Computer Science",
            end_date="2018-05"
        )
        db.add(edu1)
        db.flush()
        
        # Add skills
        skills_data = [
            ("Python", "Language", "Expert"),
            ("FastAPI", "Framework", "Expert"),
            ("PostgreSQL", "Database", "Expert"),
            ("Redis", "Database", "Advanced"),
            ("Docker", "Tool", "Expert"),
            ("JavaScript", "Language", "Advanced"),
            ("React", "Framework", "Intermediate"),
            ("AWS", "Cloud", "Advanced"),
            ("GCP", "Cloud", "Intermediate"),
            ("Kubernetes", "Tool", "Intermediate"),
            ("Celery", "Tool", "Advanced"),
            ("SQLAlchemy", "Framework", "Expert"),
            ("REST APIs", "Technology", "Expert"),
            ("Microservices", "Architecture", "Advanced"),
            ("Git", "Tool", "Expert"),
        ]
        
        for skill_name, category, proficiency in skills_data:
            skill = Skill(
                profile_id=profile.id,
                name=skill_name,
                category=category,
                proficiency=proficiency
            )
            db.add(skill)
        
        db.flush()
        
        # Add sample job
        job = Job(
            user_id=user.id,
            title="Senior Python Backend Engineer",
            company="TechCorp",
            url="https://example.com/jobs/senior-backend",
            raw_jd="""
We're looking for a Senior Python Backend Engineer to join our growing team.

Key Responsibilities:
- Design and implement scalable microservices using FastAPI
- Lead architecture decisions for distributed systems
- Mentor junior engineers and code reviews
- Optimize database performance with PostgreSQL and Redis

Requirements:
- 5+ years of Python development experience
- Expert-level knowledge of FastAPI or similar frameworks
- Strong understanding of relational databases (PostgreSQL)
- Experience with Docker and Kubernetes
- Experience with message queues (Celery, RabbitMQ)
- AWS or GCP experience
- Strong communication skills

Nice to Have:
- Experience with Kubernetes orchestration
- Open-source contributions
- Experience with event-driven architectures
- ML/AI background

Compensation:
- $180k - $220k salary
- Equity package
- Full benefits
            """
        )
        db.add(job)
        
        # Commit all
        db.commit()
        print("✓ Database seeded successfully")
        print("\nDemo Account:")
        print("  Email: demo@autoapply.ai")
        print("  Password: password123")
        print("\nDatabase includes:")
        print("  - 1 user profile")
        print("  - 2 work experiences")
        print("  - 2 projects")
        print("  - 1 education entry")
        print("  - 15 skills")
        print("  - 1 sample job posting")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        db.close()


def main():
    """Initialize and seed database."""
    init_db()
    seed_db()


if __name__ == "__main__":
    main()
