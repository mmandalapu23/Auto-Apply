"""Document rendering service (HTML → PDF)."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from app.schemas.resume import ResumeStructuredSchema


class DocumentService:
    """Helpers for rendering resume content."""

    @staticmethod
    def render_resume_html(resume: ResumeStructuredSchema) -> str:
        """Return a very lightweight HTML resume."""

        def add_section(title: str, rows: Iterable[str]) -> None:
            lines.append(f"<h2>{title}</h2>")
            lines.extend(rows)

        lines: List[str] = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '<meta charset="UTF-8">',
            "<style>body{font-family:Arial, sans-serif;margin:40px;line-height:1.6;}h2{border-bottom:1px solid #444;padding-bottom:4px;} .bullet{margin-left:16px;}</style>",
            "</head>",
            "<body>",
        ]

        header = resume.summary.text.split(" ")[0] if resume.summary and resume.summary.text else "Resume"
        lines.append(f"<h1>{header}</h1>")

        if resume.summary and resume.summary.text:
            add_section("Professional Summary", [f"<p>{resume.summary.text}</p>"])

        if resume.skills:
            skills = ", ".join(resume.skills)
            add_section("Skills", [f"<p>{skills}</p>"])

        if resume.experience:
            experience_rows: List[str] = []
            for exp in resume.experience:
                experience_rows.append(
                    "<div>" +
                    f"<strong>{exp.title}</strong> | {exp.company}<br>"
                    f"<em>{exp.start_date} - {exp.end_date or 'Present'}</em>"
                )
                for bullet in exp.bullets:
                    experience_rows.append(f"<div class='bullet'>• {bullet.text}</div>")
                experience_rows.append("</div>")
            add_section("Experience", experience_rows)

        if resume.projects:
            project_rows: List[str] = []
            for proj in resume.projects:
                project_rows.append(f"<div><strong>{proj.name}</strong></div>")
                for bullet in proj.bullets:
                    project_rows.append(f"<div class='bullet'>• {bullet.text}</div>")
            add_section("Projects", project_rows)

        if resume.education:
            edu_rows: List[str] = []
            for edu in resume.education:
                degree = f"<strong>{edu.degree}</strong> in {edu.field or 'General'}"
                dates = f"<em>{edu.graduation_date}</em>" if edu.graduation_date else ""
                edu_rows.append(f"<p>{degree}<br>{edu.institution}<br>{dates}</p>")
            add_section("Education", edu_rows)

        lines.extend(["</body>", "</html>"])
        return "\n".join(lines)

    @staticmethod
    def render_resume_ats_text(resume: ResumeStructuredSchema) -> str:
        """Produce a plaintext resume suitable for ATS uploads."""

        lines: List[str] = []

        def add_block(title: str, body: Iterable[str]) -> None:
            lines.append(title.upper())
            lines.extend(body)
            lines.append("")

        if resume.summary and resume.summary.text:
            add_block("Professional Summary", [resume.summary.text])

        if resume.skills:
            add_block("Skills", [", ".join(resume.skills)])

        if resume.experience:
            body: List[str] = []
            for exp in resume.experience:
                body.append(f"{exp.title} | {exp.company}")
                body.append(f"{exp.start_date} - {exp.end_date or 'Present'}")
                for bullet in exp.bullets:
                    body.append(f"* {bullet.text}")
                body.append("")
            add_block("Experience", body)

        if resume.projects:
            body = []
            for proj in resume.projects:
                body.append(proj.name)
                for bullet in proj.bullets:
                    body.append(f"* {bullet.text}")
                body.append("")
            add_block("Projects", body)

        if resume.education:
            body = []
            for edu in resume.education:
                body.append(f"{edu.degree} in {edu.field or 'General'}")
                body.append(edu.institution)
                if edu.graduation_date:
                    body.append(edu.graduation_date)
                body.append("")
            add_block("Education", body)

        return "\n".join(lines).strip()

    @staticmethod
    async def render_resume_pdf(resume_id: int, html_content: str) -> str:
        """Persist resume HTML and return the stored key."""

        from app.services.storage_service import get_storage_adapter

        adapter = get_storage_adapter()
        key = Path("resumes") / f"resume_{resume_id}.html"
        return adapter.store_text(str(key), html_content)
