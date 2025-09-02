#!/usr/bin/env python3
"""
Configuration and setup script for Expense Manager
"""

import os
import sys
from datetime import datetime

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    else:
        print("✅ Python version:", sys.version.split()[0])
    
    # Check if required directories exist
    required_dirs = [
        'templates',
        'static',
        'static/css',
        'static/js',
        'static/icons'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            return False
    
    # Check if required files exist
    required_files = [
        'app.py',
        'requirements.txt',
        'static/manifest.json',
        'static/sw.js',
        'static/css/style.css',
        'static/js/app.js',
        'templates/base.html'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False
    
    return True

def setup_environment():
    """Set up the development environment"""
    print("\n🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        env_content = f"""# Expense Manager Environment Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1

# Security (Change in production!)
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///expenses.db

# App Configuration
APP_NAME=Expense Manager
APP_VERSION=1.0.0
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Database
*.db
*.sqlite3

# Environment Variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Flask
instance/
.webassets-cache

# Node modules (if using npm)
node_modules/

# Temporary files
*.tmp
*.temp
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
    else:
        print("✅ .gitignore file already exists")

def display_summary():
    """Display setup summary"""
    print("\n" + "="*50)
    print("🎉 EXPENSE MANAGER SETUP COMPLETE!")
    print("="*50)
    print("\n📋 What's been set up:")
    print("   ✅ Flask web application")
    print("   ✅ SQLite database schema")
    print("   ✅ Progressive Web App (PWA)")
    print("   ✅ Mobile-first responsive design")
    print("   ✅ Admin and user management")
    print("   ✅ Expense tracking and analytics")
    print("   ✅ Savings goal management")
    print("   ✅ Dark/light mode support")
    
    print("\n🚀 To start the application:")
    print("   ./run.sh")
    print("   OR")
    print("   python3 app.py")
    
    print("\n🌐 Access URLs:")
    print("   Desktop: http://localhost:5000")
    print("   Mobile:  http://YOUR_IP:5000")
    
    print("\n📱 Mobile Features:")
    print("   • Add to home screen for app-like experience")
    print("   • Works offline with cached data")
    print("   • Touch-optimized interface")
    print("   • Bottom navigation for easy access")
    
    print("\n👤 First Time Setup:")
    print("   1. Register first user (becomes admin)")
    print("   2. Set monthly income in settings")
    print("   3. Add family members via admin panel")
    print("   4. Start tracking expenses!")
    
    print("\n💡 Pro Tips:")
    print("   • Use quick-add buttons for common expenses")
    print("   • Mark expenses as 'wanted' vs 'unwanted'")
    print("   • Check reports for spending insights")
    print("   • Set savings goals for motivation")
    
    print("\n📚 Need help? Check README.md for detailed instructions.")
    print("\n" + "="*50)

def main():
    """Main setup function"""
    print("🏠 Expense Manager Setup Script")
    print("Setting up your smart expense tracking app...\n")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed. Please fix the issues above.")
        return False
    
    # Setup environment
    setup_environment()
    
    # Create .gitignore
    create_gitignore()
    
    # Display summary
    display_summary()
    
    return True

if __name__ == "__main__":
    main()
