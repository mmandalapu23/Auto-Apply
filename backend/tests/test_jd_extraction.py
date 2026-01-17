"""Tests for JD extraction and schema validation."""
import pytest
from app.llm.pipeline import LLMPipeline
from app.schemas.jd import JDStructuredSchema


@pytest.mark.asyncio
async def test_jd_extract_schema():
    """Test JD extraction produces valid schema."""
    pipeline = LLMPipeline()
    
    sample_jd = """
    We are looking for a Senior Python Developer with 5+ years experience.
    
    Responsibilities:
    - Build scalable backend services using Python and FastAPI
    - Design and optimize database schemas in PostgreSQL
    - Collaborate with frontend team on API design
    
    Required Skills:
    - Python (must have)
    - FastAPI or Django (must have)
    - PostgreSQL (must have)
    - Docker (nice to have)
    - Kubernetes (nice to have)
    """
    
    result = await pipeline.extract_jd(sample_jd)
    
    assert isinstance(result, JDStructuredSchema)
    assert len(result.must_have_skills) > 0
    assert len(result.keywords) > 0
    assert result.years_experience == 5


def test_jd_structure_validation():
    """Test JDStructuredSchema validation."""
    data = {
        "responsibilities": [
            {"text": "Build APIs", "required": True}
        ],
        "must_have_skills": ["Python", "FastAPI"],
        "nice_to_have_skills": ["Docker"],
        "keywords": ["backend", "fastapi"],
        "seniority_signals": ["Senior"],
        "years_experience": 5
    }
    
    schema = JDStructuredSchema(**data)
    assert schema.must_have_skills == ["Python", "FastAPI"]
    assert len(schema.responsibilities) == 1
