#!/usr/bin/env python3
"""
AutoApply ATS - Project Verification Script

Run this script to verify that all project files are properly set up.
Usage: python verify_project.py
"""

import os
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def check_file(path: str) -> bool:
    """Check if a file exists."""
    return Path(path).is_file()


def check_dir(path: str) -> bool:
    """Check if a directory exists."""
    return Path(path).is_dir()


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text: str):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def verify_project_structure() -> Tuple[int, int]:
    """Verify project structure and return (passed, total)."""
    passed = 0
    total = 0
    
    print_header("Checking Project Structure")
    
    directories = [
        "backend",
        "backend/app",
        "backend/app/db",
        "backend/app/db/models",
        "backend/app/api",
        "backend/app/api/routers",
        "backend/app/services",
        "backend/app/llm",
        "backend/app/workers",
        "backend/app/web",
        "backend/app/web/templates",
        "backend/app/web/static",
        "backend/app/core",
        "backend/app/utils",
        "backend/tests",
        "backend/scripts",
        "backend/alembic",
        "docs",
    ]
    
    for directory in directories:
        total += 1
        if check_dir(directory):
            print_success(f"Directory: {directory}")
            passed += 1
        else:
            print_error(f"Directory: {directory} NOT FOUND")
    
    return passed, total


def verify_backend_files() -> Tuple[int, int]:
    """Verify backend files."""
    passed = 0
    total = 0
    
    print_header("Checking Backend Files")
    
    backend_files = [
        "backend/app/main.py",
        "backend/app/__init__.py",
        "backend/app/db/database.py",
        "backend/app/db/models/__init__.py",
        "backend/app/db/models/user.py",
        "backend/app/db/models/profile.py",
        "backend/app/db/models/job.py",
        "backend/app/db/models/resume.py",
        "backend/app/db/models/application.py",
        "backend/app/api/router.py",
        "backend/app/api/deps.py",
        "backend/app/api/routers/auth.py",
        "backend/app/api/routers/profile.py",
        "backend/app/api/routers/jobs.py",
        "backend/app/api/routers/resumes.py",
        "backend/app/api/routers/applications.py",
        "backend/app/services/auth_service.py",
        "backend/app/services/profile_service.py",
        "backend/app/services/job_service.py",
        "backend/app/llm/pipeline.py",
        "backend/app/llm/client.py",
        "backend/app/workers/celery_app.py",
        "backend/app/web/templates/layout.html",
        "backend/app/web/static/styles.css",
        "backend/pyproject.toml",
        "backend/alembic.ini",
        "backend/Makefile",
    ]
    
    for file in backend_files:
        total += 1
        if check_file(file):
            print_success(f"File: {file}")
            passed += 1
        else:
            print_error(f"File: {file} NOT FOUND")
    
    return passed, total


def verify_documentation_files() -> Tuple[int, int]:
    """Verify documentation files."""
    passed = 0
    total = 0
    
    print_header("Checking Documentation Files")
    
    doc_files = [
        "README.md",
        "GETTING_STARTED.md",
        "QUICK_REFERENCE.md",
        "WINDOWS_SETUP.md",
        "BUILD_SUMMARY.md",
        "FILE_INDEX.md",
        "MVP_COMPLETE.md",
        "IMPLEMENTATION_VALIDATION.md",
        "DEPLOYMENT_CHECKLIST.md",
        "DOCUMENTATION_INDEX.md",
        "docs/api_complete.md",
        "docs/architecture.md",
        "docs/ats_rules.md",
    ]
    
    for file in doc_files:
        total += 1
        if check_file(file):
            print_success(f"File: {file}")
            passed += 1
        else:
            print_error(f"File: {file} NOT FOUND")
    
    return passed, total


def verify_configuration_files() -> Tuple[int, int]:
    """Verify configuration files."""
    passed = 0
    total = 0
    
    print_header("Checking Configuration Files")
    
    config_files = [
        "docker-compose.yml",
        "Dockerfile",
        ".env.example",
        ".gitignore",
        "pyproject.toml",
        ".github/workflows/tests.yml",
    ]
    
    for file in config_files:
        total += 1
        if check_file(file):
            print_success(f"File: {file}")
            passed += 1
        else:
            print_warning(f"File: {file} - optional")
    
    return passed, total


def verify_test_files() -> Tuple[int, int]:
    """Verify test files."""
    passed = 0
    total = 0
    
    print_header("Checking Test Files")
    
    test_files = [
        "backend/tests/__init__.py",
        "backend/tests/conftest.py",
        "backend/tests/test_jd_extraction.py",
        "backend/tests/test_resume_validation.py",
        "backend/tests/test_matching.py",
    ]
    
    for file in test_files:
        total += 1
        if check_file(file):
            print_success(f"File: {file}")
            passed += 1
        else:
            print_warning(f"File: {file} - optional")
    
    return passed, total


def verify_dependencies() -> Tuple[int, int]:
    """Verify Python dependencies can be imported."""
    passed = 0
    total = 0
    
    print_header("Checking Python Dependencies (Optional)")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("celery", "Celery"),
        ("redis", "Redis"),
        ("psycopg2", "PostgreSQL driver"),
        ("pytest", "Pytest"),
    ]
    
    for module, name in dependencies:
        total += 1
        try:
            __import__(module)
            print_success(f"Package: {name} ({module})")
            passed += 1
        except ImportError:
            print_warning(f"Package: {name} ({module}) - not installed yet")
    
    return passed, total


def print_summary(results: List[Tuple[int, int]]):
    """Print summary of verification results."""
    total_passed = sum(p for p, t in results)
    total_checks = sum(t for p, t in results)
    
    print_header("Verification Summary")
    
    percentage = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    if percentage == 100:
        print_success(f"All checks passed! ({total_passed}/{total_checks})")
    elif percentage >= 80:
        print_success(f"Most checks passed ({total_passed}/{total_checks} - {percentage:.1f}%)")
    else:
        print_warning(f"Some checks failed ({total_passed}/{total_checks} - {percentage:.1f}%)")
    
    print(f"\n{BOLD}Status:{RESET}")
    print(f"  Passed: {GREEN}{total_passed}{RESET}")
    print(f"  Total:  {BLUE}{total_checks}{RESET}")
    print(f"  Score:  {BLUE}{percentage:.1f}%{RESET}")


def suggest_next_steps():
    """Suggest next steps based on verification."""
    print_header("Next Steps")
    
    print(f"{BOLD}1. Start the Application:{RESET}")
    print("   cd autoapply-ats")
    print("   docker-compose up -d")
    print()
    
    print(f"{BOLD}2. Access the API:{RESET}")
    print("   http://localhost:8000/docs")
    print()
    
    print(f"{BOLD}3. Login with demo credentials:{RESET}")
    print("   Email:    demo@autoapply.ai")
    print("   Password: password123")
    print()
    
    print(f"{BOLD}4. Read the documentation:{RESET}")
    print("   - GETTING_STARTED.md (first-time users)")
    print("   - QUICK_REFERENCE.md (commands)")
    print("   - docs/api_complete.md (API details)")
    print()
    
    print(f"{BOLD}5. Run tests (optional):{RESET}")
    print("   cd backend")
    print("   pytest tests/ -v")
    print()


def main():
    """Main verification function."""
    print(f"\n{BOLD}{BLUE}AutoApply ATS - Project Verification{RESET}")
    print(f"{BLUE}Version: 0.1.0{RESET}\n")
    
    results = [
        verify_project_structure(),
        verify_backend_files(),
        verify_documentation_files(),
        verify_configuration_files(),
        verify_test_files(),
        verify_dependencies(),
    ]
    
    print_summary(results)
    suggest_next_steps()
    
    total_passed = sum(p for p, t in results)
    total_checks = sum(t for p, t in results)
    
    if total_passed >= total_checks * 0.9:  # At least 90% passed
        print(f"{GREEN}✓ Project is ready to use!{RESET}\n")
        return 0
    else:
        print(f"{RED}✗ Some components may be missing{RESET}\n")
        return 1


if __name__ == "__main__":
    exit(main())
