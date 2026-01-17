"""Run all database migrations in sequence."""
import subprocess
import sys
from pathlib import Path

MIGRATIONS = [
    "migrate_job_schema.py",
    "migrate_job_indexes.py",
    "migrate_user_roles.py",
    "migrate_job_sources.py",
]

def run_migrations():
    """Execute all migration scripts."""
    script_dir = Path(__file__).parent
    
    for migration in MIGRATIONS:
        script_path = script_dir / migration
        if script_path.exists():
            print(f"\n{'='*60}")
            print(f"Running: {migration}")
            print(f"{'='*60}")
            result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
            if result.returncode != 0:
                print(f"✗ Migration failed: {migration}")
                sys.exit(1)
        else:
            print(f"⚠ Migration script not found: {migration}")
    
    print(f"\n{'='*60}")
    print("✓ All migrations completed successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_migrations()
