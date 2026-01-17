"""Matching and scoring service."""
from app.schemas.jd import EvidenceMapSchema
from app.schemas.matching import MatchingScoreSchema, MissingRequirementSchema


class MatchingService:
    """Job-candidate matching."""
    
    @staticmethod
    def calculate_match_score(evidence_map: EvidenceMapSchema) -> MatchingScoreSchema:
        """Calculate comprehensive matching score."""
        
        # Overall score from evidence map
        overall = evidence_map.match_score
        
        # Skills match
        must_have_count = len(evidence_map.jd_structured.must_have_skills)
        matched_must_have = len(evidence_map.matched_items.get("must_have_skills", []))
        skills_match = matched_must_have / must_have_count if must_have_count > 0 else 0.5
        
        # Experience match (inferred from keyword matches)
        exp_refs = evidence_map.matched_items.get("experience", [])
        experience_match = min(1.0, len(exp_refs) / 5)  # Assume 5+ experiences
        
        # Seniority match (stub)
        seniority_match = 0.7  # TODO: implement
        
        # Missing requirements
        missing_requirements = [
            MissingRequirementSchema(
                type=item["type"],
                name=item["name"],
                importance=item.get("importance", "must_have")
            )
            for item in evidence_map.missing_items
        ]
        
        # Matched and unmatched keywords
        matched_keywords = []
        unmatched_keywords = evidence_map.jd_structured.keywords.copy()
        
        for exp_ref in evidence_map.matched_items.get("experience", []):
            if exp_ref.text and exp_ref.text in unmatched_keywords:
                matched_keywords.append(exp_ref.text)
                unmatched_keywords.remove(exp_ref.text)
        
        return MatchingScoreSchema(
            overall_score=overall,
            skills_match=skills_match,
            experience_match=experience_match,
            seniority_match=seniority_match,
            missing_requirements=missing_requirements,
            matched_keywords=matched_keywords,
            unmatched_keywords=unmatched_keywords
        )
