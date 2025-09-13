#!/usr/bin/env python
"""
Complete Setup Script for Property Management System
This script will:
1. Create all necessary migrations
2. Apply migrations to database
3. Seed database with initial data
4. Create a superuser (optional)

Usage: python setup_project.py
"""

import os
import sys
import subprocess
import django

# Setup Django environment
sys.path.append('/home/mulindwa/Documents/projects/pms_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estate_mgmt.settings')

def run_command(command):
    """Run a shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e}")
        return False

def setup_database():
    """Setup database with migrations and seeding"""
    print("🚀 Setting up Property Management System Database")
    print("=" * 60)
    
    # Step 1: Create migrations
    print("\n📝 Step 1: Creating migrations...")
    apps = ['core', 'tenants', 'complaints', 'payments', 'owners', 'notifications']
    
    for app in apps:
        if not run_command(f"python manage.py makemigrations {app}"):
            print(f"⚠️  Warning: Could not create migrations for {app}")
    
    # Also try creating all migrations at once
    run_command("python manage.py makemigrations")
    
    # Step 2: Apply migrations
    print("\n🗄️  Step 2: Applying migrations to database...")
    if not run_command("python manage.py migrate"):
        print("❌ Failed to apply migrations!")
        return False
    
    # Step 3: Seed database
    print("\n🌱 Step 3: Seeding database with initial data...")
    if not run_command("python manage.py seed_db"):
        print("❌ Failed to seed database!")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Database setup completed successfully!")
    print("=" * 60)
    
    return True

def create_superuser():
    """Optionally create a superuser"""
    response = input("\n🔑 Would you like to create a superuser account? (y/n): ").lower().strip()
    if response == 'y' or response == 'yes':
        print("\n👤 Creating superuser...")
        run_command("python manage.py createsuperuser")

def main():
    """Main setup function"""
    try:
        # Setup database
        if setup_database():
            # Optionally create superuser
            create_superuser()
            
            print("\n✅ Setup Complete! Your Property Management System is ready to use.")
            print("\n🚀 Next steps:")
            print("1. Run the server: python manage.py runserver")
            print("2. Access admin panel: http://127.0.0.1:8000/admin/")
            print("3. Test API endpoints: http://127.0.0.1:8000/api/")
            print("4. Register users: POST http://127.0.0.1:8000/api/register/")
        else:
            print("❌ Setup failed. Please check the errors above.")
            
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()