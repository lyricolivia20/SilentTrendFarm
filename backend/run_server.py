#!/usr/bin/env python3
"""
Development server runner with auto-reload
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
        return True
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "../requirements.txt"])
        return False

def run_server():
    """Run the FastAPI development server"""
    # Set environment variables
    os.environ.setdefault("ENV", "development")
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("\n" + "="*50)
    print("🚀 Starting SilentTrendFarm Backend Server")
    print("="*50)
    print(f"📁 Working directory: {backend_dir}")
    print(f"🌐 Server will be available at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"📊 Alternative docs: http://localhost:8000/redoc")
    print("="*50 + "\n")
    
    # Run the server
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info"
    ])

if __name__ == "__main__":
    if not check_dependencies():
        check_dependencies()  # Try again after installation
    run_server()
