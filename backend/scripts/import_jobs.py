"""Import real jobs from Greenhouse job boards."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.job_source_service import JobSourceService
from app.db.session import SessionLocal
from app.db.models import Job


async def import_jobs():
    """Import jobs from various Greenhouse boards."""
    db = SessionLocal()
    
    # Delete the hardcoded test job
    deleted = db.query(Job).filter(Job.title == 'Senior Python Backend Engineer').delete()
    if deleted:
        print(f"Removed {deleted} sample job(s)")
    db.commit()
    
    # Companies with public Greenhouse boards
    companies = [
        ('airbnb', 'Airbnb'),
        ('discord', 'Discord'),
        ('stripe', 'Stripe'),
        ('figma', 'Figma'),
        ('coinbase', 'Coinbase'),
        ('twitch', 'Twitch'),
        ('spotify', 'Spotify'),
        ('squarespace', 'Squarespace'),
        ('lyft', 'Lyft'),
        ('instacart', 'Instacart'),
        ('robinhood', 'Robinhood'),
        ('gusto', 'Gusto'),
        ('flexport', 'Flexport'),
        ('benchling', 'Benchling'),
        ('ramp', 'Ramp'),
        ('brex', 'Brex'),
        ('chime', 'Chime'),
        ('airtable', 'Airtable'),
        ('faire', 'Faire'),
        ('nerdwallet', 'NerdWallet'),
    ]
    
    # Keywords for Data/Software roles
    keywords = [
        'data engineer', 'data analyst', 'data scientist',
        'software engineer', 'backend', 'python', 'full stack',
        'machine learning', 'ml engineer', 'platform engineer'
    ]
    
    total = 0
    for board_token, company_name in companies:
        print(f"\nFetching from {company_name}...")
        try:
            jobs = await JobSourceService.fetch_greenhouse_jobs(
                board_token=board_token,
                company=company_name,
                limit=15,
                include_keywords=keywords
            )
            for j in jobs:
                existing = db.query(Job).filter(Job.url == j['url']).first()
                if not existing:
                    job = Job(
                        user_id=1,
                        title=j['title'],
                        company=j['company'],
                        url=j['url'],
                        raw_jd=j['raw_jd']
                    )
                    db.add(job)
                    total += 1
                    print(f"  + {j['title']}")
            if not jobs:
                print(f"  (no matching roles found)")
        except Exception as e:
            print(f"  ! Error: {e}")
    
    db.commit()
    db.close()
    print(f"\n✓ Imported {total} jobs from job portals!")


if __name__ == "__main__":
    asyncio.run(import_jobs())
