"""Tests for resume validation."""
import pytest
from app.schemas.resume import ResumeStructuredSchema, ResumeSummarySchema
from app.schemas.resume import ResumeExperienceSchema, ResumeBulletSchema
from app.schemas.jd import EvidenceRefSchema
from app.llm.validators import validate_no_fabrication, validate_ats_formatting


def test_resume_fabrication_check():
    """Test that resumes without evidence refs are flagged."""
    resume_data = {
        "experience": [
            {
                "company": "TechCorp",
                "title": "Senior Developer",
                "start_date": "01/2020",
                "end_date": "12/2023",
                "bullets": [
                    {
                        "text": "Led team of 10 engineers",
                        "evidence_refs": []  # No evidence!
                    }
                ]
            }
        ]
    }
    
    passed, issues = validate_no_fabrication(resume_data)
    assert not passed
    assert len(issues) > 0


def test_resume_valid_fabrication_check():
    """Test that resumes with evidence refs pass."""
    resume_data = {
        "experience": [
            {
                "company": "TechCorp",
                "title": "Senior Developer",
                "start_date": "01/2020",
                "end_date": "12/2023",
                "bullets": [
                    {
                        "text": "Led team of 10 engineers",
                        "evidence_refs": [
                            {"type": "experience", "id": 1, "bullet_idx": 0}
                        ]
                    }
                ]
            }
        ]
    }
    
    passed, issues = validate_no_fabrication(resume_data)
    assert passed


def test_ats_formatting_validation():
    """Test ATS formatting checks."""
    bad_resume = """
    Senior Developer
    Tech Skills | Python | FastAPI | PostgreSQL
    
    Experience
    +-----------+--------+--------+
    | Company   | Title  | Dates  |
    +-----------+--------+--------+
    """
    
    passed, issues = validate_ats_formatting(bad_resume)
    assert not passed
    
    
    good_resume = """
    SENIOR DEVELOPER
    
    SKILLS
    Python, FastAPI, PostgreSQL
    
    EXPERIENCE
    Senior Developer | TechCorp
    01/2020 - 12/2023
    * Led development of microservices
    """
    
    passed, issues = validate_ats_formatting(good_resume)
    assert passed
