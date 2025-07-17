#!/usr/bin/env python3
"""
Setup script for the Utility Consumption Prediction System.
This script sets up the environment and creates necessary directories.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'data/processed',
        'data/external',
        'models',
        'logs',
        'config',
        'scripts/utils'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✓ Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False
    return True

def setup_jupyter():
    """Set up Jupyter notebook configuration."""
    try:
        subprocess.run([sys.executable, '-m', 'ipykernel', 'install', '--user', '--name', 'utility-env'], 
                      check=True)
        print("✓ Jupyter kernel installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error setting up Jupyter: {e}")
        return False
    return True

def create_env_file():
    """Create a .env file with default configurations."""
    env_content = """# Environment Configuration
DATABASE_URL=sqlite:///./utility_consumption.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
MODEL_PATH=models/utility_consumption_model.pkl
DATA_PATH=data/raw/Utility_consumption.csv
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✓ Created .env file")

def main():
    """Main setup function."""
    print("Setting up Utility Consumption Prediction System...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup Jupyter
    setup_jupyter()
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the backend: python backend/api/main.py")
    print("2. Run the frontend: cd frontend && npm start")
    print("3. Open Jupyter: jupyter notebook")
    print("4. Or use Docker: docker-compose -f docker/docker-compose.yml up")

if __name__ == "__main__":
    main() 