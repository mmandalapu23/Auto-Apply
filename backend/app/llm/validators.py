"""Resume validators."""
from typing import List, Tuple


def validate_no_fabrication(resume_data: dict) -> Tuple[bool, List[str]]:
    """Ensure all resume bullets are grounded in evidence."""
    issues = []
    
    for exp in resume_data.get("experience", []):
        for bullet in exp.get("bullets", []):
            if not bullet.get("evidence_refs"):
                issues.append(f"Fabricated claim: {bullet.get('text')}")
    
    return len(issues) == 0, issues


def validate_ats_formatting(resume_text: str) -> Tuple[bool, List[str]]:
    """Check ATS-friendly formatting."""
    issues = []
    
    # Check for common ATS issues
    if "|" in resume_text and resume_text.count("|") > 3:
        issues.append("Too many pipe characters - may confuse ATS")
    
    if "\t" in resume_text:
        issues.append("Contains tabs - use spaces instead")
    
    # Check for tables/columns
    if "+" in resume_text or "-" * 5 in resume_text:
        issues.append("Possible table/column formatting - use plain text")
    
    return len(issues) == 0, issues


def validate_consistent_dates(resume_data: dict) -> Tuple[bool, List[str]]:
    """Check date consistency."""
    issues = []
    
    for exp in resume_data.get("experience", []):
        start = exp.get("start_date", "")
        end = exp.get("end_date", "")
        if end and start > end:
            issues.append(f"Invalid dates: {start} to {end}")
    
    return len(issues) == 0, issues
