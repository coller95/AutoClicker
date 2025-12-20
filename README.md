# AutoClicker

A powerful Windows desktop application for recording and replaying mouse clicks and keyboard inputs with customizable hotkeys.

## Features

- 🎬 **Record & Replay**: Record mouse clicks and keyboard inputs, then replay them automatically
- 🔁 **Loop Control**: Set the number of loops (1-100) or run infinitely
- ⌨️ **Customizable Hotkeys**: Configure your preferred hotkeys for record, play, and stop
- 📝 **Event Log**: View all recorded events with timestamps
- 🎮 **Easy Controls**: Simple GUI with clear status indicators
- 🚀 **Lightweight**: Standalone executable, no installation required

## Default Hotkeys

- **F1**: Toggle recording
- **F2**: Toggle playback
- **ESC**: Force stop playback

## Installation

### Option 1: Download Pre-built Executable (Recommended)
1. Download `AutoClicker.exe` from the [Releases](../../releases) page
2. Run the executable - no installation needed!

### Option 2: Run from Source
1. Clone this repository:
   ```bash
   git clone https://github.com/coller95/AutoClicker.git
   cd AutoClicker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python autoclicker.py
   ```

## Usage

1. **Recording**:
   - Click "Start Recording" or press **F1** (default)
   - Perform your mouse clicks and keyboard inputs
   - Click "Stop Recording" or press **F1** again

2. **Playback**:
   - Set the desired number of loops (0 = infinite)
   - Click "Play Recording" or press **F2**
   - To stop early, click "Stop Playing", press **F2**, or press **ESC**

3. **Customizing Hotkeys**:
   - Click on any hotkey button (e.g., "F1", "F2", "ESC")
   - Press your desired key to set a new hotkey

4. **Clearing Recording**:
   - Click "Clear Recording" to remove all recorded events

## Building from Source

To build the executable yourself:

```bash
python build.py
```

The executable will be created in the `dist/` directory.

## Requirements

- Windows OS
- Python 3.7+ (for running from source)
- Dependencies:
  - pynput==1.7.6
  - pyinstaller (for building)

## Use Cases

- Automating repetitive tasks
- Testing applications
- Game automation
- Data entry automation
- Demonstration recording

## Limitations

- Windows only
- Some games with anti-cheat systems may block input simulation
- Administrator privileges may be required for some applications

## Safety Notice

⚠️ **Important**: This tool simulates keyboard and mouse input. Use responsibly and ensure:
- You have permission to automate the target application
- You comply with the terms of service of any software you're using
- You don't use this for cheating or unauthorized access

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

Made with ❤️ for automation enthusiasts
