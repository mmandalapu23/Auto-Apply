"""External job source integrations (e.g., Greenhouse)."""
import re
from html import unescape
from typing import List, Dict, Optional

import httpx


class JobSourceService:
    """Fetch job postings from external sources."""

    @staticmethod
    async def fetch_greenhouse_jobs(
        board_token: str,
        company: Optional[str] = None,
        limit: int = 20,
        include_keywords: Optional[list[str]] = None,
    ) -> List[Dict[str, Optional[str]]]:
        """Fetch jobs from a Greenhouse board.

        Args:
            board_token: Greenhouse board token, e.g., "airbnb".
            company: Optional override for company name (fallback to board_token).
            limit: Max number of jobs to return.
        """
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        params = {"content": "true"}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()

        jobs = payload.get("jobs", [])
        results: List[Dict[str, Optional[str]]] = []
        for job in jobs[:limit]:
            html_content = job.get("content") or ""
            title = job.get("title") or "Untitled role"

            if include_keywords:
                lowered = title.lower()
                if not any(keyword.lower() in lowered for keyword in include_keywords):
                    continue

            results.append(
                {
                    "title": title,
                    "company": company or board_token,
                    "url": job.get("absolute_url"),
                    "raw_jd": JobSourceService._strip_html(html_content),
                }
            )
        return results

    @staticmethod
    def _strip_html(html: str) -> str:
        """Lightweight HTML -> text conversion."""
        text = unescape(html)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<p\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()
