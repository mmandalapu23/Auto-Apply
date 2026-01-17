"""FlexJobs API integration for remote job listings."""
import re
from datetime import datetime
from typing import Dict, List, Optional

import httpx


class FlexJobsService:
    """Fetches remote job postings from FlexJobs."""

    FLEXJOBS_API = "https://api.flexjobs.com/jobs"
    
    @classmethod
    async def fetch_jobs(
        cls,
        api_key: str,
        category: Optional[str] = None,
        job_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Retrieve remote jobs from FlexJobs API.
        
        Args:
            api_key: FlexJobs API key
            category: Job category filter (e.g., "data", "writing")
            job_type: Job type filter (e.g., "full-time", "part-time")
            limit: Maximum jobs to return
        
        Returns:
            List of job dicts with standard job fields
        """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        params = {
            "limit": limit,
            "remote": True,  # FlexJobs specializes in remote jobs
        }
        
        if category:
            params["category"] = category
        if job_type:
            params["job_type"] = job_type
        
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(
                    cls.FLEXJOBS_API,
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
            
            jobs = data.get("results", [])
            results: List[Dict] = []
            
            for job in jobs:
                results.append({
                    "title": job.get("title", "Untitled"),
                    "company": job.get("company", "Unknown"),
                    "url": job.get("url"),
                    "raw_jd": job.get("description", ""),
                    "location": job.get("location", "Remote"),
                    "country": job.get("country", "USA"),
                    "is_remote": True,  # FlexJobs only lists remote jobs
                    "employment_type": cls._normalize_job_type(job.get("job_type")),
                    "salary_range": job.get("salary", None),
                    "source": "flexjobs",
                    "source_job_id": str(job.get("id", "")),
                    "posting_date": cls._parse_date(job.get("posted_date")),
                })
            
            return results
        
        except Exception as e:
            print(f"Error fetching FlexJobs listings: {e}")
            return []
    
    @staticmethod
    def _normalize_job_type(job_type: Optional[str]) -> str:
        """Normalize job type to standard employment type."""
        if not job_type:
            return "Full-time"
        
        job_type_lower = job_type.lower()
        
        if "full" in job_type_lower or "permanent" in job_type_lower:
            return "Full-time"
        elif "part" in job_type_lower:
            return "Part-time"
        elif "contract" in job_type_lower or "freelance" in job_type_lower:
            return "Contract"
        elif "internship" in job_type_lower:
            return "Internship"
        
        return "Full-time"
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from FlexJobs response."""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common date formats
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return None
