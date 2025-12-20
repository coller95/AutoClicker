#!/usr/bin/env python
"""
Run script for AutoClicker
"""
import os
import sys
import subprocess

def main():
    print("Starting AutoClicker...")
    
    # Check if autoclicker.py exists
    if not os.path.exists("autoclicker.py"):
        print("Error: autoclicker.py not found!")
        sys.exit(1)
    
    # Run the application
    try:
        subprocess.run([sys.executable, "autoclicker.py"])
    except KeyboardInterrupt:
        print("\nAutoclicker closed.")
    except Exception as e:
        print(f"Error running autoclicker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
