"""External job source integrations for Greenhouse and other boards."""
import re
from datetime import datetime
from html import unescape
from typing import Dict, List, Optional

import httpx


class JobSourceService:
    """Fetches job postings from external job boards."""

    GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    
    # Role categorization keywords
    ROLE_CATEGORIES = {
        "Data Engineer": ["data engineer", "data engineering", "etl", "data pipeline"],
        "Data Analyst": ["data analyst", "business analyst", "analytics"],
        "Data Scientist": ["data scientist", "machine learning", "ml engineer"],
        "Software Developer": ["software engineer", "backend", "frontend", "full stack", "developer"],
        "DevOps Engineer": ["devops", "sre", "site reliability", "infrastructure"],
        "Product Manager": ["product manager", "product owner", "pm"],
        "Other": []
    }

    @classmethod
    async def fetch_greenhouse_jobs(
        cls,
        board_token: str,
        company: Optional[str] = None,
        limit: int = 20,
        include_keywords: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Retrieve jobs from a Greenhouse company board with comprehensive data extraction.

        Args:
            board_token: Board identifier (e.g., "airbnb", "stripe").
            company: Display name override; defaults to board_token.
            limit: Maximum jobs to return.
            include_keywords: Filter titles containing these words.

        Returns:
            List of job dicts with comprehensive job details.
        """
        url = cls.GREENHOUSE_API.format(token=board_token)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params={"content": "true"})
            response.raise_for_status()
            data = response.json()

        jobs = data.get("jobs", [])
        results: List[Dict] = []

        for job in jobs:
            if len(results) >= limit:
                break

            title = job.get("title", "Untitled")

            if include_keywords:
                title_lower = title.lower()
                if not any(kw.lower() in title_lower for kw in include_keywords):
                    continue

            # Extract location info
            location_obj = job.get("location", {})
            location = location_obj.get("name", "") if location_obj else ""
            
            # Parse comprehensive job data
            html_content = job.get("content") or ""
            raw_jd = cls._html_to_text(html_content)
            
            # Extract sections
            responsibilities, skills_info = cls._extract_job_sections(raw_jd)
            
            # Determine role category
            role_category = cls._categorize_role(title)
            
            # Try to extract employment type
            employment_type = cls._extract_employment_type(raw_jd, title)
            
            # Extract country from location
            country = cls._extract_country(location)
            
            # Detect remote status
            is_remote = cls._is_remote_job(location, raw_jd)
            
            results.append({
                "title": title,
                "company": company or board_token,
                "url": job.get("absolute_url"),
                "raw_jd": raw_jd,
                "location": location,
                "country": country,
                "is_remote": is_remote,
                "employment_type": employment_type,
                "responsibilities": responsibilities,
                "required_skills": skills_info.get("required"),
                "preferred_skills": skills_info.get("preferred"),
                "role_category": role_category,
                "source": "greenhouse",
                "source_job_id": str(job.get("id", "")),
                "posting_date": cls._parse_date(job.get("updated_at")),
            })

        return results

    @staticmethod
    def _categorize_role(title: str) -> str:
        """Determine role category based on title keywords."""
        title_lower = title.lower()
        
        for category, keywords in JobSourceService.ROLE_CATEGORIES.items():
            if any(kw in title_lower for kw in keywords):
                return category
        
        return "Other"

    @staticmethod
    def _extract_employment_type(jd_text: str, title: str) -> Optional[str]:
        """Extract employment type from job description or title."""
        text = (jd_text + " " + title).lower()
        
        if "intern" in text:
            return "Internship"
        elif "contract" in text or "contractor" in text:
            return "Contract"
        elif "part-time" in text or "part time" in text:
            return "Part-time"
        elif "full-time" in text or "full time" in text or "fulltime" in text:
            return "Full-time"
        
        return "Full-time"  # Default assumption

    @staticmethod
    def _extract_country(location: str) -> Optional[str]:
        """Extract country from location string."""
        if not location:
            return None
        
        location_lower = location.lower()
        
        # Common country patterns
        country_keywords = {
            "USA": ["united states", "usa", "u.s.", "california", "new york", "texas", "seattle", "boston", "austin", "san francisco"],
            "UK": ["united kingdom", "uk", "london", "manchester", "edinburgh", "cambridge"],
            "India": ["india", "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad", "pune", "chennai"],
            "Canada": ["canada", "toronto", "vancouver", "montreal", "ottawa"],
            "Germany": ["germany", "berlin", "munich", "frankfurt"],
            "Remote": ["remote", "anywhere"],
        }
        
        for country, keywords in country_keywords.items():
            if any(kw in location_lower for kw in keywords):
                return country
        
        return "Other"

    @staticmethod
    def _is_remote_job(location: str, jd_text: str) -> bool:
        """Determine if job is remote."""
        combined = (location + " " + jd_text).lower()
        remote_keywords = ["remote", "work from home", "wfh", "distributed", "anywhere"]
        return any(kw in combined for kw in remote_keywords)

    @staticmethod
    def _extract_job_sections(jd_text: str) -> tuple:
        """Extract responsibilities and skills from job description."""
        # Look for common section headers
        responsibilities = None
        skills_required = None
        skills_preferred = None
        
        # Split by common headers (case-insensitive)
        sections = re.split(r'\n(?:Responsibilities|What You\'ll Do|Your Role|Duties|Key Responsibilities)[:|\n]', jd_text, flags=re.IGNORECASE)
        if len(sections) > 1:
            # Extract first section after header
            resp_section = sections[1].split('\n\n')[0:3]  # Get first few paragraphs
            responsibilities = '\n'.join(resp_section).strip()
        
        # Extract skills sections
        required_match = re.search(r'(?:Required Skills|Requirements|Must Have|Qualifications)[:|\n](.*?)(?:\n\n|Preferred|Nice to Have|$)', jd_text, re.IGNORECASE | re.DOTALL)
        if required_match:
            skills_required = required_match.group(1).strip()
        
        preferred_match = re.search(r'(?:Preferred Skills|Nice to Have|Bonus|Preferred Qualifications)[:|\n](.*?)(?:\n\n|$)', jd_text, re.IGNORECASE | re.DOTALL)
        if preferred_match:
            skills_preferred = preferred_match.group(1).strip()
        
        return responsibilities, {
            "required": skills_required,
            "preferred": skills_preferred
        }

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string to datetime."""
        if not date_str:
            return None
        try:
            # Greenhouse returns ISO format like "2024-01-15T10:30:00Z"
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML content to plain text."""
        text = unescape(html)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<p\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()
