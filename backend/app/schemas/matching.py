"""Matching and scoring schemas."""
from pydantic import BaseModel
from typing import List, Optional


class MissingRequirementSchema(BaseModel):
    """Missing requirement or gap."""
    type: str  # "skill", "experience", "certification"
    name: str
    importance: str = "must_have"  # "must_have" or "nice_to_have"


class MatchingScoreSchema(BaseModel):
    """Job-candidate matching score and analysis."""
    overall_score: float  # 0-1
    skills_match: float
    experience_match: float
    seniority_match: float
    missing_requirements: List[MissingRequirementSchema] = []
    matched_keywords: List[str] = []
    unmatched_keywords: List[str] = []
