"""Migrate existing job data to new schema."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, engine
from sqlalchemy import text


def migrate_schema():
    """Add new columns to jobs table."""
    db = SessionLocal()
    
    try:
        # Add new columns if they don't exist
        columns_to_add = [
            ("location", "VARCHAR"),
            ("country", "VARCHAR"),
            ("is_remote", "BOOLEAN DEFAULT FALSE"),
            ("employment_type", "VARCHAR"),
            ("salary_range", "VARCHAR"),
            ("responsibilities", "TEXT"),
            ("required_skills", "TEXT"),
            ("preferred_skills", "TEXT"),
            ("source", "VARCHAR"),
            ("source_job_id", "VARCHAR"),
            ("posting_date", "DATETIME"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("last_synced_at", "DATETIME"),
            ("role_category", "VARCHAR"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                db.execute(text(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}"))
                print(f"✓ Added column: {col_name}")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"  Column {col_name} already exists, skipping")
                else:
                    print(f"✗ Error adding {col_name}: {e}")
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_source_job_id ON jobs(source_job_id)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_role_category ON jobs(role_category)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)",
        ]
        
        for idx_sql in indexes:
            try:
                db.execute(text(idx_sql))
            except Exception as e:
                print(f"  Index creation note: {e}")
        
        db.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_schema()
