#!/usr/bin/env python3
"""
BloodReport AI Setup Script
Automates the installation and setup process for the full-stack application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_node_version():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/")
    return False

def install_python_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def install_frontend_dependencies():
    """Install frontend dependencies."""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    success = run_command("npm install", "Installing frontend dependencies")
    os.chdir("..")
    return success

def create_env_file():
    """Create .env file with default configuration."""
    env_content = """# Database Configuration
DATABASE_URL=mysql://bloodreport_user:bloodreport_password@localhost/bloodreport_ai

# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists, skipping creation")
        return True
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_data_directory():
    """Create data directory for uploaded files."""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print("✅ Created data directory")
    else:
        print("✅ Data directory already exists")
    return True

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Configure your .env file with your actual credentials")
    print("2. Set up MySQL database:")
    print("   - Create database: CREATE DATABASE bloodreport_ai;")
    print("   - Create user: CREATE USER 'bloodreport_user'@'localhost' IDENTIFIED BY 'bloodreport_password';")
    print("   - Grant privileges: GRANT ALL PRIVILEGES ON bloodreport_ai.* TO 'bloodreport_user'@'localhost';")
    print("3. Start Redis server")
    print("4. Start the application:")
    print("   - Backend: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("   - Celery: celery -A celery_app worker --loglevel=info")
    print("   - Frontend: cd frontend && npm start")
    print("\nFor detailed instructions, see README.md")
    print("="*60)

def main():
    """Main setup function."""
    print("🚀 BloodReport AI Setup Script")
    print("="*40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    if not install_frontend_dependencies():
        sys.exit(1)
    
    # Create necessary files and directories
    if not create_env_file():
        sys.exit(1)
    
    if not create_data_directory():
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main() 