"""Add role column to users table for RBAC (role-based access control)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from sqlalchemy import text

def migrate():
    """Add role column and set defaults."""
    db = SessionLocal()
    try:
        # Check if role column exists
        check_sql = "PRAGMA table_info(users)"
        result = db.execute(text(check_sql))
        columns = [row[1] for row in result]
        
        if "role" not in columns:
            # Add role column with default value
            db.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"))
            print("✓ Added 'role' column to users table")
            
            # Create index on role for faster queries
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_user_role ON users(role)"))
            print("✓ Created index on users.role")
        else:
            print("✓ 'role' column already exists")
        
        db.commit()
        print("✓ User role migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
