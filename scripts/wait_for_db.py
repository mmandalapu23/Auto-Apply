#!/usr/bin/env python
"""Wait for database to be ready before starting the app."""
import os
import time
import psycopg2
from psycopg2 import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/autoapply")

def wait_for_db():
    """Poll the database until it responds."""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("✓ Database is ready!")
            return True
        except OperationalError:
            attempt += 1
            print(f"Waiting for database... ({attempt}/{max_attempts})")
            time.sleep(1)
    
    print("✗ Database did not respond in time")
    return False

if __name__ == "__main__":
    if not wait_for_db():
        exit(1)
