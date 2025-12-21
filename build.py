#!/usr/bin/env python
"""
Build script for AutoClicker
Packages the application into a standalone executable
"""
import os
import sys
import shutil
import subprocess

def main():
    print("=" * 50)
    print("Building AutoClicker Executable")
    print("=" * 50)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("[FAIL] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed")
    
    print()
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    print("[OK] Cleanup complete")
    print()
    
    # Build executable
    print("Building executable...")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "AutoClicker.spec",
        "--clean"
    ]
    
    result = subprocess.run(cmd)
    print()
    
    if result.returncode == 0:
        print("=" * 50)
        print("[OK] Build successful!")
        print("Executable location: dist/AutoClicker.exe")
        print("=" * 50)
        
        # Show file size
        exe_path = os.path.join("dist", "AutoClicker.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"File size: {size_mb:.2f} MB")
    else:
        print("=" * 50)
        print("[FAIL] Build failed! Check errors above.")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()
