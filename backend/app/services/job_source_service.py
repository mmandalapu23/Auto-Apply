"""External job source integrations for Greenhouse and other boards."""
import re
from html import unescape
from typing import Dict, List, Optional

import httpx


class JobSourceService:
    """Fetches job postings from external job boards."""

    GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"

    @classmethod
    async def fetch_greenhouse_jobs(
        cls,
        board_token: str,
        company: Optional[str] = None,
        limit: int = 20,
        include_keywords: Optional[List[str]] = None,
    ) -> List[Dict[str, Optional[str]]]:
        """
        Retrieve jobs from a Greenhouse company board.

        Args:
            board_token: Board identifier (e.g., "airbnb", "stripe").
            company: Display name override; defaults to board_token.
            limit: Maximum jobs to return.
            include_keywords: Filter titles containing these words.

        Returns:
            List of job dicts with title, company, url, and raw_jd.
        """
        url = cls.GREENHOUSE_API.format(token=board_token)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params={"content": "true"})
            response.raise_for_status()
            data = response.json()

        jobs = data.get("jobs", [])
        results: List[Dict[str, Optional[str]]] = []

        for job in jobs:
            if len(results) >= limit:
                break

            title = job.get("title", "Untitled")

            if include_keywords:
                title_lower = title.lower()
                if not any(kw.lower() in title_lower for kw in include_keywords):
                    continue

            results.append({
                "title": title,
                "company": company or board_token,
                "url": job.get("absolute_url"),
                "raw_jd": cls._html_to_text(job.get("content") or ""),
            })

        return results

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML content to plain text."""
        text = unescape(html)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<p\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()
