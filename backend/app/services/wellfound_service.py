"""Wellfound (formerly AngelList) job board integration."""
import re
from datetime import datetime
from typing import Dict, List, Optional

import httpx


class WellfoundService:
    """Fetches job postings from Wellfound (AngelList)."""

    WELLFOUND_API = "https://api.wellfound.com/jobs"
    
    @classmethod
    async def fetch_jobs(
        cls,
        role: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Retrieve jobs from Wellfound API.
        
        Args:
            role: Job role/title filter
            location: Location filter
            limit: Maximum jobs to return
        
        Returns:
            List of job dicts with standard job fields
        """
        params = {
            "page": 1,
            "per_page": limit,
        }
        
        if role:
            params["role"] = role
        if location:
            params["locations"] = location
        
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(cls.WELLFOUND_API, params=params)
                response.raise_for_status()
                data = response.json()
            
            jobs = data.get("jobs", [])
            results: List[Dict] = []
            
            for job in jobs:
                results.append({
                    "title": job.get("title", "Untitled"),
                    "company": job.get("company", {}).get("name", "Unknown"),
                    "url": job.get("url"),
                    "raw_jd": job.get("description", ""),
                    "location": job.get("location", ""),
                    "country": cls._extract_country(job.get("location", "")),
                    "is_remote": job.get("remote", False),
                    "employment_type": job.get("type", "Full-time"),
                    "salary_range": cls._extract_salary(job),
                    "source": "wellfound",
                    "source_job_id": str(job.get("id", "")),
                    "posting_date": cls._parse_date(job.get("created_at")),
                })
            
            return results
        
        except Exception as e:
            print(f"Error fetching Wellfound jobs: {e}")
            return []
    
    @staticmethod
    def _extract_country(location: str) -> Optional[str]:
        """Extract country from location."""
        if not location:
            return None
        
        location_lower = location.lower()
        
        country_keywords = {
            "USA": ["united states", "usa", "us", "california", "new york", "texas"],
            "UK": ["united kingdom", "uk", "london"],
            "India": ["india", "bangalore", "mumbai"],
            "Canada": ["canada", "toronto"],
            "Remote": ["remote", "anywhere"],
        }
        
        for country, keywords in country_keywords.items():
            if any(kw in location_lower for kw in keywords):
                return country
        
        return "Other"
    
    @staticmethod
    def _extract_salary(job: Dict) -> Optional[str]:
        """Extract salary from job dict."""
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        currency = job.get("salary_currency", "$")
        
        if salary_min and salary_max:
            return f"{currency}{salary_min:,} - {currency}{salary_max:,}"
        elif salary_min:
            return f"{currency}{salary_min:,}+"
        
        return None
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
