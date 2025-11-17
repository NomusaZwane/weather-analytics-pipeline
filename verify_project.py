# verify_project.py - Check if all project files exist
import os

required_files = [
    'weather_etl.py',
    'weather_dashboard.py', 
    'weather_scheduler.py',
    'simple_dashboard.py',
    'requirements.txt',
    '.gitignore',
    'README.md'
]

print("🔍 Verifying Project Structure...")
print("=" * 40)

all_good = True
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING")
        all_good = False

print("=" * 40)
if all_good:
    print("🎉 All files present! Project structure is complete!")
    print("🚀 Ready for GitHub deployment!")
else:
    print("⚠️  Some files are missing. Please create them.")