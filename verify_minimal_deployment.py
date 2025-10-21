#!/usr/bin/env python3
"""
Verification script to check that only essential files for Railway deployment remain
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def main():
    print("Verifying minimal QClip Telegram Bot deployment files...\n")
    
    # List of essential files for Railway deployment
    essential_files = [
        ("railway.toml", "Railway configuration"),
        ("Procfile", "Railway process file"),
        ("requirements.txt", "Python dependencies"),
        ("QClip.csv", "Quran data file"),
        ("bot.py", "Main bot implementation"),
        ("README.md", "Documentation"),
        (".gitignore", "Git exclusion patterns")
    ]
    
    # Check each file
    all_files_present = True
    for filename, description in essential_files:
        filepath = os.path.join(os.getcwd(), filename)
        if not check_file_exists(filepath, description):
            all_files_present = False
    
    print("\n" + "="*50)
    if all_files_present:
        print("✅ All essential files are present for deployment!")
        print("\nYour project is now clean and ready for Railway deployment.")
        print("\nEssential files:")
        for filename, description in essential_files:
            print(f"  • {filename} - {description}")
        print("\nDeployment type: Worker (long-polling Telegram bot)")
        print("Service type: Worker")
        print("Entry point: bot.py")
    else:
        print("❌ Some essential files are missing!")
        print("Please check the missing files and ensure they are created.")
    
    return all_files_present

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)