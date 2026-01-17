"""Development server launcher for VS Code."""
import subprocess
import sys
from pathlib import Path

def main():
    """Launch development server with all components."""
    backend_path = Path(__file__).parent / "backend"
    
    print("🚀 AutoApply ATS Development Server")
    print("=" * 50)
    
    # Change to backend directory
    import os
    os.chdir(backend_path)
    
    # Start uvicorn
    print("\n📡 Starting FastAPI server on http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print("\n   Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload",
             "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_path)
        )
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
