"""Migrate: Add job_sources table for multi-source support."""
import sys
from datetime import datetime

try:
    import sqlite3
    from pathlib import Path
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def migrate_job_sources():
    """Add job_sources table to database."""
    db_path = Path(__file__).parent.parent / "autoapply.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create job_sources table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            display_name VARCHAR(100) NOT NULL,
            api_endpoint VARCHAR(500),
            api_key VARCHAR(500),
            is_enabled BOOLEAN DEFAULT 1,
            is_configured BOOLEAN DEFAULT 0,
            last_sync_at DATETIME,
            last_sync_status VARCHAR(50) DEFAULT 'pending',
            last_error VARCHAR(500),
            sync_interval_hours INTEGER DEFAULT 6,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create index on name
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_job_sources_name ON job_sources(name)
        """)
        
        # Create index on is_enabled
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_job_sources_enabled ON job_sources(is_enabled)
        """)
        
        # Insert default sources
        default_sources = [
            ("greenhouse", "Greenhouse", "https://api.greenhouse.io/v1/jobs", None, 1, 0),
            ("wellfound", "Wellfound", "https://api.wellfound.com/jobs", None, 1, 0),
            ("flexjobs", "FlexJobs", "https://api.flexjobs.com/jobs", None, 0, 0),
            ("workday", "Workday", None, None, 0, 0),
        ]
        
        for source in default_sources:
            cursor.execute("""
            INSERT OR IGNORE INTO job_sources 
            (name, display_name, api_endpoint, api_key, is_enabled, is_configured)
            VALUES (?, ?, ?, ?, ?, ?)
            """, source)
        
        conn.commit()
        print("✓ Created job_sources table")
        print("✓ Added default job sources (greenhouse enabled)")
        print("✓ Created indexes on job_sources table")
        return True
    
    except Exception as e:
        print(f"❌ Error creating job_sources table: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate_job_sources()
    if success:
        print("✓ Job sources migration completed successfully!")
        sys.exit(0)
    else:
        print("✗ Job sources migration failed!")
        sys.exit(1)
