# Changelog

All notable changes to AutoClicker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
