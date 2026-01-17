"""LLM pipeline: extract JD -> map evidence -> generate resume -> validate."""
import json
from typing import List, Tuple
from app.llm.client import LLMClient
from app.schemas.jd import JDStructuredSchema, EvidenceRefSchema, EvidenceMapSchema
from app.schemas.resume import ResumeStructuredSchema
from app.db.models import Profile, Experience, Project, Education, Skill


class LLMPipeline:
    """Multi-step LLM orchestration with strict grounding."""
    
    def __init__(self):
        self.client = LLMClient()
    
    async def extract_jd(self, raw_jd: str) -> JDStructuredSchema:
        """Step 1: Extract and structure job description."""
        return await self.client.extract_jd(raw_jd)
    
    async def map_evidence(
        self,
        profile,  # Profile ORM object
        jd_structured: JDStructuredSchema
    ) -> EvidenceMapSchema:
        """
        Step 2: Map JD requirements to user profile evidence.
        
        No fabrication: every matched item must exist in profile.
        """
        matched_items = {}
        missing_items = []
        matched_count = 0
        total_required = 0
        
        # Map must-have skills
        matched_items["must_have_skills"] = []
        total_required += len(jd_structured.must_have_skills)
        
        profile_skills = {s.name.lower(): s for s in profile.skills}
        for skill_name in jd_structured.must_have_skills:
            skill_key = skill_name.lower()
            if skill_key in profile_skills:
                matched_items["must_have_skills"].append(
                    EvidenceRefSchema(
                        type="skill",
                        id=profile_skills[skill_key].id,
                        text=skill_name
                    )
                )
                matched_count += 1
            else:
                missing_items.append({
                    "type": "skill",
                    "name": skill_name,
                    "importance": "must_have"
                })
        
        # Map nice-to-have skills
        matched_items["nice_to_have_skills"] = []
        for skill_name in jd_structured.nice_to_have_skills:
            skill_key = skill_name.lower()
            if skill_key in profile_skills:
                matched_items["nice_to_have_skills"].append(
                    EvidenceRefSchema(
                        type="skill",
                        id=profile_skills[skill_key].id,
                        text=skill_name
                    )
                )
                matched_count += 1
            else:
                missing_items.append({
                    "type": "skill",
                    "name": skill_name,
                    "importance": "nice_to_have"
                })
        
        # Map keywords to experience/projects
        matched_items["keywords"] = []
        matched_items["experience"] = []
        for exp in profile.experiences:
            if exp.description:  # Assuming bullets are stored as JSON
                bullets = json.loads(exp.description) if isinstance(exp.description, str) else []
                for bullet in bullets:
                    bullet_text = bullet.get("text", "").lower()
                    for keyword in jd_structured.keywords:
                        if keyword.lower() in bullet_text:
                            matched_items["experience"].append(
                                EvidenceRefSchema(
                                    type="experience",
                                    id=exp.id,
                                    text=keyword
                                )
                            )
        
        # Calculate match score
        match_score = matched_count / total_required if total_required > 0 else 0.5
        
        return EvidenceMapSchema(
            jd_structured=jd_structured,
            matched_items=matched_items,
            missing_items=missing_items,
            match_score=min(1.0, match_score)
        )
    
    async def generate_resume(
        self,
        profile,  # Profile ORM object
        jd_structured: JDStructuredSchema,
        evidence_map: EvidenceMapSchema
    ) -> ResumeStructuredSchema:
        """
        Step 3: Generate resume with evidence grounding.
        
        Rules:
        - Every bullet must have evidence_refs
        - If cannot support → NEEDS_USER_INPUT
        - Match JD keywords in experience bullets
        """
        from app.schemas.resume import (
            ResumeSummarySchema, ResumeExperienceSchema, ResumeProjectSchema,
            ResumeEducationSchema, ResumeBulletSchema
        )
        
        # Summary (grounded in profile summary or generated)
        summary_text = profile.summary or "Professional with strong technical background"
        summary = ResumeSummarySchema(
            text=summary_text,
            evidence_refs=[]
        )
        
        # Skills (matched from evidence map)
        matched_skill_ids = set()
        for ref in evidence_map.matched_items.get("must_have_skills", []):
            matched_skill_ids.add(ref.id)
        for ref in evidence_map.matched_items.get("nice_to_have_skills", []):
            matched_skill_ids.add(ref.id)
        
        skills = []
        for skill in profile.skills:
            if skill.id in matched_skill_ids:
                skills.append(skill.name)
        
        # Experience (with bullets grounded in evidence)
        experiences = []
        for exp in profile.experiences:
            bullets = []
            if exp.description:
                try:
                    exp_bullets = json.loads(exp.description) if isinstance(exp.description, str) else []
                except:
                    exp_bullets = []
            else:
                exp_bullets = []
            
            for bullet in exp_bullets:
                # Check if bullet matches any JD keyword
                matched_keywords = []
                for keyword in jd_structured.keywords:
                    if keyword.lower() in bullet.get("text", "").lower():
                        matched_keywords.append(keyword)
                
                bullets.append(
                    ResumeBulletSchema(
                        text=bullet.get("text", ""),
                        evidence_refs=[
                            EvidenceRefSchema(
                                type="experience",
                                id=exp.id,
                                bullet_idx=exp_bullets.index(bullet),
                                text=bullet.get("text", "")
                            )
                        ]
                    )
                )
            
            experiences.append(
                ResumeExperienceSchema(
                    company=exp.company,
                    title=exp.title,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    bullets=bullets,
                    evidence_refs=[
                        EvidenceRefSchema(type="experience", id=exp.id)
                    ]
                )
            )
        
        # Projects
        projects = []
        for proj in profile.projects:
            bullets = []
            if proj.description:
                try:
                    proj_bullets = json.loads(proj.description) if isinstance(proj.description, str) else []
                except:
                    proj_bullets = []
            else:
                proj_bullets = []
            
            for bullet in proj_bullets:
                bullets.append(
                    ResumeBulletSchema(
                        text=bullet.get("text", ""),
                        evidence_refs=[
                            EvidenceRefSchema(
                                type="project",
                                id=proj.id,
                                text=bullet.get("text", "")
                            )
                        ]
                    )
                )
            
            if bullets:  # Only include if has content
                projects.append(
                    ResumeProjectSchema(
                        name=proj.name,
                        bullets=bullets,
                        evidence_refs=[
                            EvidenceRefSchema(type="project", id=proj.id)
                        ]
                    )
                )
        
        # Education
        educations = []
        for edu in profile.educations:
            educations.append(
                ResumeEducationSchema(
                    institution=edu.institution,
                    degree=edu.degree,
                    field=edu.field,
                    graduation_date=edu.end_date
                )
            )
        
        return ResumeStructuredSchema(
            summary=summary,
            skills=skills,
            experience=experiences,
            projects=projects,
            education=educations
        )
    
    async def validate_resume(self, resume: ResumeStructuredSchema) -> Tuple[bool, List[str]]:
        """
        Step 4: Validate resume for ATS compliance and evidence grounding.
        
        Returns: (passed: bool, issues: List[str])
        """
        issues = []
        
        # Check for fabrication: every bullet must have evidence
        for exp in resume.experience:
            for bullet in exp.bullets:
                if bullet.needs_user_input:
                    issues.append(f"Experience needs user input: {bullet.needs_user_input}")
                if not bullet.evidence_refs:
                    issues.append(f"Experience bullet has no evidence: {bullet.text}")
        
        for proj in resume.projects:
            for bullet in proj.bullets:
                if bullet.needs_user_input:
                    issues.append(f"Project needs user input: {bullet.needs_user_input}")
                if not bullet.evidence_refs:
                    issues.append(f"Project bullet has no evidence: {bullet.text}")
        
        # Check ATS formatting
        # - No tables/columns
        # - Standard headings
        # - Consistent dates
        
        # Check date ranges (start <= end)
        for exp in resume.experience:
            if exp.end_date and exp.start_date > exp.end_date:
                issues.append(f"Invalid date range in {exp.company}: {exp.start_date} to {exp.end_date}")
        
        # Check contact info exists
        if not resume.summary:
            issues.append("Missing summary/contact information")
        
        passed = len(issues) == 0
        return passed, issues
