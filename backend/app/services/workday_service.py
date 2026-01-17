"""Workday job board API integration for enterprise job listings."""
import re
from datetime import datetime
from typing import Dict, List, Optional

import httpx


class WorkdayService:
    """Fetches jobs from companies using Workday job boards."""

    @classmethod
    async def fetch_jobs(
        cls,
        company_domain: str,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Retrieve jobs from a company's Workday job board.
        
        Args:
            company_domain: Company's Workday domain (e.g., "company.wd1.myworkdayjobs.com")
            keywords: Search keywords
            location: Location filter
            limit: Maximum jobs to return
        
        Returns:
            List of job dicts with standard job fields
        """
        workday_api = f"https://{company_domain}/wday/cxs/jobs"
        
        params = {
            "limit": limit,
        }
        
        if keywords:
            params["q"] = keywords
        if location:
            params["locations"] = location
        
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(workday_api, params=params)
                response.raise_for_status()
                data = response.json()
            
            jobs = data.get("jobs", [])
            results: List[Dict] = []
            
            # Extract company name from domain
            company_name = company_domain.split(".")[0].title()
            
            for job in jobs:
                results.append({
                    "title": job.get("title", "Untitled"),
                    "company": company_name,
                    "url": job.get("url"),
                    "raw_jd": cls._extract_description(job),
                    "location": job.get("location", ""),
                    "country": cls._extract_country(job.get("location", "")),
                    "is_remote": cls._is_remote(job),
                    "employment_type": cls._extract_employment_type(job),
                    "salary_range": cls._extract_salary(job),
                    "source": "workday",
                    "source_job_id": str(job.get("id", "")),
                    "posting_date": cls._parse_date(job.get("posted_on")),
                })
            
            return results
        
        except Exception as e:
            print(f"Error fetching Workday jobs for {company_domain}: {e}")
            return []
    
    @staticmethod
    def _extract_description(job: Dict) -> str:
        """Extract job description."""
        return job.get("description") or job.get("summary") or ""
    
    @staticmethod
    def _is_remote(job: Dict) -> bool:
        """Detect if job is remote."""
        location = (job.get("location", "") or "").lower()
        description = (job.get("description", "") or "").lower()
        
        remote_keywords = ["remote", "work from home", "virtual", "anywhere"]
        
        if any(kw in location for kw in remote_keywords):
            return True
        
        if any(kw in description for kw in remote_keywords):
            return True
        
        return False
    
    @staticmethod
    def _extract_employment_type(job: Dict) -> str:
        """Extract employment type."""
        job_type = job.get("employment_type", "").lower()
        
        if "full" in job_type:
            return "Full-time"
        elif "part" in job_type:
            return "Part-time"
        elif "contract" in job_type:
            return "Contract"
        elif "temp" in job_type:
            return "Contract"
        elif "internship" in job_type:
            return "Internship"
        
        return "Unknown"
    
    @staticmethod
    def _extract_salary(job: Dict) -> Optional[str]:
        """Extract salary range."""
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        currency = job.get("currency", "$")
        
        if salary_min and salary_max:
            return f"{currency}{salary_min:,} - {currency}{salary_max:,}"
        elif salary_min:
            return f"{currency}{salary_min:,}+"
        elif job.get("salary"):
            return job.get("salary")
        
        return None
    
    @staticmethod
    def _extract_country(location: str) -> Optional[str]:
        """Extract country from location."""
        if not location:
            return None
        
        location_lower = location.lower()
        
        country_keywords = {
            "USA": ["united states", "usa", "us", "ca", "tx", "ny", "dc"],
            "UK": ["united kingdom", "uk", "london"],
            "Canada": ["canada", "toronto"],
            "India": ["india", "bangalore"],
            "Remote": ["remote"],
        }
        
        for country, keywords in country_keywords.items():
            if any(kw in location_lower for kw in keywords):
                return country
        
        return "Other"
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date from Workday response."""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return None
