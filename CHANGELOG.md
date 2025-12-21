# Changelog

All notable changes to AutoClicker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Draft Releases**: Releases are now created as drafts for safety
- **Robust Versioning**: Fixed release workflow to correctly read version numbers

## [1.7.0] - 2025-12-21

### Added
- **Auto-Versioning**: bump2version + git tags + GitHub Actions workflow
- Version shown in window title and build output
- Convenience script: `bump_version.py`

### Developer Experience
- Single source of truth: `__version__.py`
- Automatic tags like `v1.7.0`

## [1.5.0] - 2025-12-21

### Added
- **Save/Load Configuration**: Hotkey and timing settings now save with recordings
- Configuration persistence in .aclk files
- Automatic settings restore when loading recordings

### Improved
- Better user experience with preserved settings
- Seamless workflow when switching between recordings

## [1.4.0] - 2025-12-21

### Added
- **Save/Load Recordings**: Export and import recordings with .aclk file format
- **Side-by-Side Layout**: Improved UI with better space utilization
- **Icon Support**: Application icon in window title bar and taskbar
- File dialogs for saving and loading recordings

### Improved
- Professional file format for recording management
- Better organization of UI elements
- Enhanced visual appearance

## [1.3.0] - 2025-12-21

### Added
- **Visual Status Indicators**: Compact banner at top-left shows current mode
- **Screen Border Frame**: Thin colored border frames entire screen during recording/playing
- **Window Title Updates**: Title bar shows current status (RECORDING/PLAYING/SPAM CLICKING)
- **Always-on-top Indicators**: Status banner stays visible over all other windows

### Features
- 🔴 Red border and banner when recording
- 🔵 Blue border and banner when playing back
- 🟠 Orange border and banner when spam clicking
- Professional recording indicator that's always visible

### Improved
- Better visual feedback for user awareness
- Clear indication of active automation state

## [1.2.0] - 2025-12-21

### Added
- **Playback Speed Control**: Adjust replay speed from 0.1x to 10x (default 1.0x)
- **Delay Between Loops**: Set delay in seconds between loop repetitions (0-60 seconds)
- **Infinite Loop Default**: Loop count now defaults to 0 (infinite) for convenience
- **Resizable Window**: Window is now resizable with larger default size (650x650)

### Improved
- UI layout expanded to accommodate new controls
- Better default settings for typical use cases

### Fixed
- UI elements no longer fall outside window bounds
- Window minimum size set to prevent layout issues

## [1.1.0] - 2025-12-21

### Added
- **Rapid-Fire Spam Click**: Press F3 to toggle ultra-fast left clicking (100 clicks per second)
- Configurable spam click hotkey in settings panel
- Visual status indicator when spam clicking is active
- Thread-based spam click implementation for smooth performance

### Features
- **Spam Click Mode**: Activate with F3 (default) for rapid-fire left clicking
- **Safety**: Cannot spam click while recording to prevent conflicts
- **Performance**: Optimized 0.01s click interval (100 CPS) for maximum speed
- **Integration**: Works independently alongside record/playback features

## [1.0.0] - 2025-12-20

### Added
- Initial release of AutoClicker
- Mouse click recording and playback functionality
- Keyboard input recording and playback functionality
- Customizable hotkeys for record, play, and stop actions
- Loop control (1-100 loops or infinite)
- Event log viewer with timestamps
- Clear recording functionality
- Real-time status updates
- GUI with intuitive controls
- Standalone executable build system

### Features
- **Recording**: Capture mouse clicks and keyboard inputs with precise timing
- **Playback**: Replay recorded actions with accurate timing
- **Hotkey Support**: Default hotkeys (F1, F2, ESC) with customization
- **Loop Options**: Set specific loop count or run indefinitely
- **Event Tracking**: View all recorded events with timestamps in scrollable log
- **Safety Controls**: Force stop with ESC key, prevents recording during playback

### Technical Details
- Built with Python and Tkinter
- Uses pynput library for input simulation
- PyInstaller for executable creation
- Windows-only support

### Known Limitations
- Windows OS only
- May not work with some anti-cheat protected applications
- Requires appropriate permissions for input simulation

---

## Release Notes

### Version 1.0.0
This is the first stable release of AutoClicker. The application has been tested for basic functionality and is ready for general use. Future releases will focus on:
- Cross-platform support
- Additional recording options
- Macro management features
- Profile saving/loading
- Performance improvements

For bug reports or feature requests, please visit the [GitHub Issues](../../issues) page.
