"""Tests for matching and scoring."""
import pytest
from app.schemas.jd import EvidenceMapSchema, JDStructuredSchema
from app.services.matching_service import MatchingService


def test_match_score_calculation():
    """Test match score calculation."""
    jd_structured = JDStructuredSchema(
        must_have_skills=["Python", "FastAPI", "PostgreSQL"],
        nice_to_have_skills=["Docker"],
        keywords=["backend", "api", "database"],
        responsibilities=[],
        seniority_signals=["Senior"]
    )
    
    evidence_map = EvidenceMapSchema(
        jd_structured=jd_structured,
        matched_items={
            "must_have_skills": [
                {"type": "skill", "id": 1, "text": "Python"},
                {"type": "skill", "id": 2, "text": "FastAPI"}
            ],
            "nice_to_have_skills": [
                {"type": "skill", "id": 3, "text": "Docker"}
            ]
        },
        missing_items=[
            {"type": "skill", "name": "PostgreSQL", "importance": "must_have"}
        ],
        match_score=0.67
    )
    
    score = MatchingService.calculate_match_score(evidence_map)
    
    assert score.overall_score == 0.67
    assert score.skills_match < 1.0  # Missing PostgreSQL
    assert len(score.missing_requirements) == 1
