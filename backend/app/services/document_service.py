"""Document rendering service (HTML → PDF)."""
from pathlib import Path
from app.schemas.resume import ResumeStructuredSchema


class DocumentService:
    """Document generation and rendering."""
    
    @staticmethod
    def render_resume_html(resume: ResumeStructuredSchema) -> str:
        """Render resume to HTML."""
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '<meta charset="UTF-8">',
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }",
            "h1 { margin: 0; }",
            "h2 { margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #333; }",
            ".contact { margin-bottom: 20px; }",
            ".job { margin-bottom: 15px; }",
            ".bullet { margin-left: 20px; }",
            "em { color: #666; }",
            "</style>",
            "</head>",
            "<body>",
        ]
        
        # Header with contact
        lines.append("<div class='contact'>")
        lines.append(f"<h1>{resume.summary.text.split()[0] if resume.summary.text else 'Resume'}</h1>")
        lines.append("</div>")
        
        # Summary
        if resume.summary and resume.summary.text:
            lines.append("<h2>PROFESSIONAL SUMMARY</h2>")
            lines.append(f"<p>{resume.summary.text}</p>")
        
        # Skills
        if resume.skills:
            lines.append("<h2>SKILLS</h2>")
            skills_text = ", ".join(resume.skills)
            lines.append(f"<p>{skills_text}</p>")
        
        # Experience
        if resume.experience:
            lines.append("<h2>EXPERIENCE</h2>")
            for exp in resume.experience:
                lines.append("<div class='job'>")
                lines.append(f"<strong>{exp.title}</strong> | {exp.company}")
                lines.append(f"<br><em>{exp.start_date} - {exp.end_date or 'Present'}</em>")
                if exp.bullets:
                    for bullet in exp.bullets:
                        lines.append(f"<div class='bullet'>• {bullet.text}</div>")
                lines.append("</div>")
        
        # Projects
        if resume.projects:
            lines.append("<h2>PROJECTS</h2>")
            for proj in resume.projects:
                lines.append("<div class='job'>")
                lines.append(f"<strong>{proj.name}</strong>")
                if proj.bullets:
                    for bullet in proj.bullets:
                        lines.append(f"<div class='bullet'>• {bullet.text}</div>")
                lines.append("</div>")
        
        # Education
        if resume.education:
            lines.append("<h2>EDUCATION</h2>")
            for edu in resume.education:
                lines.append(f"<p><strong>{edu.degree}</strong> in {edu.field or 'General'}")
                lines.append(f"<br>{edu.institution}")
                if edu.graduation_date:
                    lines.append(f"<br><em>{edu.graduation_date}</em>")
                lines.append("</p>")
        
        lines.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def render_resume_ats_text(resume: ResumeStructuredSchema) -> str:
        """Render resume as plain ATS text."""
        lines = []
        
        # Summary
        if resume.summary and resume.summary.text:
            lines.append("PROFESSIONAL SUMMARY")
            lines.append(resume.summary.text)
            lines.append("")
        
        # Skills
        if resume.skills:
            lines.append("SKILLS")
            lines.append(", ".join(resume.skills))
            lines.append("")
        
        # Experience
        if resume.experience:
            lines.append("EXPERIENCE")
            for exp in resume.experience:
                lines.append(f"{exp.title} | {exp.company}")
                lines.append(f"{exp.start_date} - {exp.end_date or 'Present'}")
                for bullet in exp.bullets:
                    lines.append(f"* {bullet.text}")
                lines.append("")
        
        # Projects
        if resume.projects:
            lines.append("PROJECTS")
            for proj in resume.projects:
                lines.append(f"{proj.name}")
                for bullet in proj.bullets:
                    lines.append(f"* {bullet.text}")
                lines.append("")
        
        # Education
        if resume.education:
            lines.append("EDUCATION")
            for edu in resume.education:
                lines.append(f"{edu.degree} in {edu.field or 'General'}")
                lines.append(edu.institution)
                if edu.graduation_date:
                    lines.append(edu.graduation_date)
                lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    async def render_resume_pdf(resume_id: int, html_content: str) -> str:
        """
        Render HTML to PDF using Playwright.
        
        For MVP: save as HTML with .pdf extension
        Later: use Playwright to convert
        """
        # Use storage adapter so we can swap local disk for S3/R2.
        from app.services.storage_service import get_storage_adapter

        adapter = get_storage_adapter()
        key = Path("resumes") / f"resume_{resume_id}.html"  # Store as HTML for MVP
        stored_key = adapter.store_text(str(key), html_content)
        return stored_key
