#!/usr/bin/env python3
"""Startup script for Buddi Tokenization PoC."""

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  No .env file found. Creating from template...")
        if os.path.exists("env.example"):
            subprocess.run(["cp", "env.example", ".env"])
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your configuration")
        else:
            print("❌ No env.example file found")
            return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Environment check passed")
    return True


def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = "venv"
    
    if not os.path.exists(venv_path):
        print("🐍 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
        return True


def get_python_executable():
    """Get the Python executable path (virtual environment if available)."""
    venv_path = "venv"
    if os.path.exists(venv_path):
        if os.name == 'nt':  # Windows
            return os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/macOS
            return os.path.join(venv_path, "bin", "python")
    return sys.executable


def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    
    # Create virtual environment first
    if not create_virtual_environment():
        return False
    
    python_exe = get_python_executable()
    
    try:
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_database():
    """Set up the database."""
    print("🗄️  Setting up database...")
    
    python_exe = get_python_executable()
    
    try:
        subprocess.run([python_exe, "scripts/setup_db.py"], check=True)
        print("✅ Database setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False


def create_demo_data():
    """Create demo data for testing."""
    print("🎭 Creating demo data...")
    
    python_exe = get_python_executable()
    
    try:
        subprocess.run([python_exe, "scripts/demo_data.py"], check=True)
        print("✅ Demo data created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo data creation failed: {e}")
        return False


def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    python_exe = get_python_executable()
    
    try:
        subprocess.run([
            python_exe, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")


def main():
    """Main startup function."""
    print("🎯 Buddi Tokenization PoC - Startup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Create demo data
    if not create_demo_data():
        print("⚠️  Demo data creation failed, but continuing...")
    
    # Start server
    start_server()


if __name__ == "__main__":
    main()
