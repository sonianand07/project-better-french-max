#!/usr/bin/env python3
"""
Better French Max - Automated System Setup
Quick setup script to configure the automated system
"""

import os
import shutil
import sys
from pathlib import Path

def setup_automated_system():
    """Setup the automated system with necessary configurations"""
    
    print("🚀 Setting up Better French Max Automated System")
    print("=" * 60)
    
    # 1. Copy API configuration from manual system
    print("1️⃣ Setting up API configuration...")
    
    manual_config = "../02_Scripts/config.py"
    auto_config = "config/api_config.py"
    
    if os.path.exists(manual_config):
        try:
            # Create config directory
            os.makedirs("config", exist_ok=True)
            
            # Copy the working config
            shutil.copy2(manual_config, auto_config)
            print(f"   ✅ Copied API config from {manual_config}")
            
        except Exception as e:
            print(f"   ❌ Failed to copy config: {e}")
            print("   🔧 Please manually copy your config.py to config/api_config.py")
    else:
        print(f"   ⚠️ Manual config not found at {manual_config}")
        print("   🔧 Please create config/api_config.py with your API key")
    
    # 2. Create necessary directories
    print("\n2️⃣ Creating directory structure...")
    
    directories = [
        "data/live",
        "data/processed", 
        "data/archive",
        "logs",
        "scripts",
        "website",
        "config"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   📁 Created: {directory}")
    
    # 3. Install dependencies
    print("\n3️⃣ Installing dependencies...")
    print("   📦 Run: pip install -r requirements.txt")
    
    # 4. Setup verification
    print("\n4️⃣ Verifying setup...")
    
    required_files = [
        "config/automation.py",
        "scripts/scheduler_main.py", 
        "website/index.html",
        "requirements.txt"
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_good = False
    
    # 5. Next steps
    print("\n" + "=" * 60)
    
    if all_good:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Test configuration: python3 config/automation.py")
        print("   3. Start automation: python3 scripts/scheduler_main.py")
        print("   4. Start website: cd website && python3 -m http.server 8001")
        print("\n📊 Monitor logs: tail -f logs/automation.log")
        
    else:
        print("⚠️ Setup incomplete - some files are missing")
        print("🔧 Please complete the setup manually")
    
    print("\n📖 Full documentation: README.md")
    
def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Better French Max - Automated System Setup")
        print("Usage: python3 setup.py")
        print("This script sets up the automated system configuration")
        return
    
    setup_automated_system()

if __name__ == "__main__":
    main() 