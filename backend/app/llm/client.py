"""LLM client adapter (stub for MVP)."""
from app.core.config import settings
from app.schemas.jd import JDStructuredSchema, ResponsibilitySchema
import json


class LLMClient:
    """LLM provider adapter."""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
    
    async def extract_jd(self, raw_jd: str) -> JDStructuredSchema:
        """
        Extract structured JD from raw text.
        
        For MVP: parse using regex/heuristics. 
        Later: call actual LLM.
        """
        # Stub implementation - would call OpenAI/Anthropic
        responsibilities = self._extract_responsibilities(raw_jd)
        must_have_skills = self._extract_skills(raw_jd, "must have")
        nice_to_have_skills = self._extract_skills(raw_jd, "nice to have")
        keywords = self._extract_keywords(raw_jd)
        seniority_signals = self._extract_seniority(raw_jd)
        years_exp = self._extract_years_experience(raw_jd)
        
        return JDStructuredSchema(
            responsibilities=responsibilities,
            must_have_skills=must_have_skills,
            nice_to_have_skills=nice_to_have_skills,
            keywords=keywords,
            seniority_signals=seniority_signals,
            years_experience=years_exp,
        )
    
    async def generate_resume_text(self, profile_data: dict, jd_data: dict, evidence_map: dict) -> str:
        """Generate professional resume text with evidence grounding."""
        # For MVP: simple template
        # Later: call LLM with strict schema enforcement
        lines = []
        
        # Name and contact
        lines.append(profile_data.get("email", ""))
        if profile_data.get("phone"):
            lines.append(f" | {profile_data['phone']}")
        if profile_data.get("location"):
            lines.append(f" | {profile_data['location']}")
        
        # Summary
        if profile_data.get("summary"):
            lines.append("\nSUMMARY")
            lines.append(profile_data["summary"])
        
        # Skills
        if profile_data.get("skills"):
            lines.append("\nSKILLS")
            lines.append(", ".join([s.get("name", "") for s in profile_data["skills"]]))
        
        # Experience
        if profile_data.get("experiences"):
            lines.append("\nEXPERIENCE")
            for exp in profile_data["experiences"]:
                lines.append(f"\n{exp.get('title', '')} | {exp.get('company', '')}")
                lines.append(f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}")
                if exp.get("bullets"):
                    for bullet in exp["bullets"]:
                        lines.append(f"• {bullet.get('text', '')}")
        
        # Education
        if profile_data.get("educations"):
            lines.append("\nEDUCATION")
            for edu in profile_data["educations"]:
                lines.append(f"{edu.get('degree', '')} in {edu.get('field', '')}")
                lines.append(edu.get("institution", ""))
        
        return "\n".join(lines)
    
    def _extract_responsibilities(self, text: str) -> list:
        """Extract responsibilities from JD."""
        responsibilities = []
        # Stub: look for common keywords
        for line in text.split("\n"):
            if any(kw in line.lower() for kw in ["responsible", "duties", "required", "will"]):
                responsibilities.append(
                    ResponsibilitySchema(text=line.strip(), required=True)
                )
        return responsibilities if responsibilities else [ResponsibilitySchema(text="Review job description")]
    
    def _extract_skills(self, text: str, skill_type: str) -> list:
        """Extract skills from JD."""
        # Stub: common tech stack
        common_skills = [
            "python", "java", "javascript", "typescript", "sql", "aws", "docker",
            "kubernetes", "react", "nodejs", "fastapi", "postgresql", "mongodb"
        ]
        found = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill in text_lower:
                found.append(skill)
        return found[:5]  # Return top 5
    
    def _extract_keywords(self, text: str) -> list:
        """Extract keywords."""
        # Stub: just split and filter
        words = text.split()
        keywords = [w.strip(",.!?;:") for w in words if len(w) > 5]
        return list(set(keywords))[:10]
    
    def _extract_seniority(self, text: str) -> list:
        """Extract seniority indicators."""
        seniority = []
        text_lower = text.lower()
        if any(s in text_lower for s in ["senior", "lead", "principal"]):
            seniority.append("Senior level")
        elif any(s in text_lower for s in ["junior", "entry"]):
            seniority.append("Junior level")
        else:
            seniority.append("Mid-level")
        return seniority
    
    def _extract_years_experience(self, text: str) -> int:
        """Extract years of experience requirement."""
        # Stub: look for "X years"
        import re
        match = re.search(r"(\d+)\s+years?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 3  # Default
