# AutoClicker - Version Management Guide

## Auto-Versioning System

This project uses **bump2version** for automated version management with git integration.

### Version Format

We follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.3.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (e.g., 1.3.0 → 1.4.0)
- **PATCH**: Bug fixes (e.g., 1.3.0 → 1.3.1)

### Quick Start

1. **Install bump2version** (if not already installed):
   ```bash
   pip install bump2version
   ```

2. **Bump version** using the convenience script:
   ```bash
   # For bug fixes
   python bump_version.py patch

   # For new features
   python bump_version.py minor

   # For breaking changes
   python bump_version.py major
   ```

3. **Push changes**:
   ```bash
   git push
   git push --tags
   ```

### What Happens Automatically

When you bump a version:
- ✅ `__version__.py` is updated
- ✅ `CHANGELOG.md` gets a new version entry
- ✅ Changes are committed to git
- ✅ A git tag is created (e.g., `v1.3.1`)

### Manual Commands

You can also use bump2version directly:

```bash
# Bump and commit
bumpversion patch
bumpversion minor
bumpversion major

# Dry run (see what would change)
bumpversion --dry-run --verbose patch
```

### Version Display

The version is automatically displayed in:
- Window title: "AutoClicker v1.3.0"
- Build output: "Building AutoClicker v1.3.0 Executable"

### Files Modified by Version Bumping

- `__version__.py` - Source of truth for version
- `CHANGELOG.md` - Automatic version header insertion
- `.bumpversion.cfg` - Configuration (already set up)

### Best Practices

1. **Before bumping**: Ensure all changes are committed
2. **Update CHANGELOG**: Add your changes under `## [Unreleased]` section
3. **Bump version**: Run `python bump_version.py [type]`
4. **Review**: Check with `git log -1` and `git tag`
5. **Push**: Push commits and tags to remote

### Example Workflow

```bash
# 1. Make changes to code
# ... edit files ...

# 2. Update CHANGELOG.md under [Unreleased] section
# ... add your changes ...

# 3. Bump version (this auto-commits)
python bump_version.py minor

# 4. Push to remote
git push && git push --tags

# 5. Build release
python build.py
```

### Troubleshooting

**Q: "bumpversion: command not found"**  
A: Run `pip install bump2version`

**Q: "Working directory is not clean"**  
A: Commit or stash your changes first

**Q: How do I see current version?**  
A: Check `__version__.py` or run the app

**Q: Can I bump version manually?**  
A: Yes, edit `__version__.py`, but you'll miss auto-commit and tagging
