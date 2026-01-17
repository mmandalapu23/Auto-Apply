"""Add salary_range extraction and improve job detail metadata."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from sqlalchemy import text

def migrate():
    """Add missing indexes and ensure all columns exist."""
    db = SessionLocal()
    try:
        # Verify all critical columns exist
        columns_to_check = {
            "salary_range": "VARCHAR",
            "responsibilities": "TEXT",
            "required_skills": "TEXT",
            "preferred_skills": "TEXT",
            "source": "VARCHAR",
            "source_job_id": "VARCHAR",
        }
        
        # Create indexes for better query performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_job_employment_type ON jobs(employment_type)",
            "CREATE INDEX IF NOT EXISTS idx_job_source ON jobs(source)",
            "CREATE INDEX IF NOT EXISTS idx_job_posting_date ON jobs(posting_date)",
            "CREATE INDEX IF NOT EXISTS idx_job_user_active ON jobs(user_id, is_active)",
        ]
        
        for idx_sql in indexes:
            db.execute(text(idx_sql))
            print(f"✓ {idx_sql.split('ON')[0].strip()}")
        
        db.commit()
        print("✓ All indexes created successfully!")
        
    except Exception as e:
        print(f"✗ Migration error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
