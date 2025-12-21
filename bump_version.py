#!/usr/bin/env python
"""
Version Bump Script for AutoClicker
Automates version bumping with git tags

Usage:
    python bump_version.py patch   # 1.3.0 -> 1.3.1
    python bump_version.py minor   # 1.3.0 -> 1.4.0
    python bump_version.py major   # 1.3.0 -> 2.0.0
"""
import sys
import subprocess

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['patch', 'minor', 'major']:
        print("Usage: python bump_version.py [patch|minor|major]")
        print()
        print("Examples:")
        print("  python bump_version.py patch   # Bug fixes (1.3.0 -> 1.3.1)")
        print("  python bump_version.py minor   # New features (1.3.0 -> 1.4.0)")
        print("  python bump_version.py major   # Breaking changes (1.3.0 -> 2.0.0)")
        sys.exit(1)
    
    part = sys.argv[1]
    
    print(f"Bumping {part} version...")
    print()
    
    # Run bump2version
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bumpversion", part],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✓ Version bumped successfully!")
        print("✓ Changes committed to git")
        print("✓ Git tag created")
        print()
        print("Next steps:")
        print("  1. Review the changes: git log -1")
        print("  2. Push to remote: git push && git push --tags")
        
    except subprocess.CalledProcessError as e:
        print("✗ Error bumping version:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("✗ bump2version not installed!")
        print("Install it with: pip install bump2version")
        sys.exit(1)

if __name__ == "__main__":
    main()
