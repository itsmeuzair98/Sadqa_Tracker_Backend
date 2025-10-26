#!/usr/bin/env python3
"""
Development startup script for Sadqa Tracker Backend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Sadqa Tracker Backend Setup")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  .env file not found!")
        print("Please copy .env.example to .env and configure your settings:")
        print("  cp .env.example .env")
        print("Then edit .env with your database URL and Google OAuth credentials.")
        return 1
    
    # Check if virtual environment is activated
    if not os.environ.get('VIRTUAL_ENV'):
        print("\n⚠️  Virtual environment not detected!")
        print("Please activate your virtual environment first:")
        print("  python -m venv venv")
        print("  # On Windows: venv\\Scripts\\activate")
        print("  # On macOS/Linux: source venv/bin/activate")
        return 1
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return 1
    
    # Initialize database
    print("\n🗄️  Database Setup")
    run_command("alembic upgrade head", "Running database migrations")
    
    # Start the server
    print("\n🌟 Starting FastAPI server...")
    print("API will be available at: http://0.0.0.0:8000")
    print("Documentation will be available at: http://0.0.0.0:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            "python", "main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
