"""Main window UI for AutoClicker application - simplified version using widgets."""

import tkinter as tk
import os

from __version__ import __version__
from core.app_controller import AppController
from ui.widgets.control_widget import ControlWidget
from ui.widgets.settings_widget import SettingsWidget
from ui.widgets.hotkey_widget import HotkeyWidget
from ui.widgets.status_widget import StatusWidget
from ui.widgets.event_log_widget import EventLogWidget
from ui.widgets.hotkey_info_widget import HotkeyInfoWidget
from utils.constants import Window, Fonts


class MainWindow:
    """Main application window for AutoClicker."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        
        # Initialize controller
        self.controller = AppController(root)
        
        # Setup UI
        self._setup_ui()
        
        # Connect widgets to controller
        self._connect_controller()
        
        # Start the controller
        self.controller.start()
    
    def _setup_window(self):
        """Configure the main window."""
        self.root.title(f"AutoClicker v{__version__}")
        self.root.geometry(f"{Window.DEFAULT_WIDTH}x{Window.DEFAULT_HEIGHT}")
        self.root.resizable(True, True)
        self.root.minsize(Window.MIN_WIDTH, Window.MIN_HEIGHT)
        
        # Set window icon
        icon_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        )
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Title
        title_label = tk.Label(
            self.root,
            text="AutoClicker with Recording",
            font=Fonts.TITLE
        )
        title_label.pack(pady=5)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left Panel
        left_panel = tk.Frame(main_container, width=Window.LEFT_PANEL_WIDTH)
        left_panel.pack(side="left", fill="both", padx=(5, 2))
        left_panel.pack_propagate(False)
        
        # Get hotkeys for initial display
        hotkeys = self.controller.get_hotkeys()
        
        # Control Widget
        self.control_widget = ControlWidget(
            left_panel,
            record_hotkey=hotkeys.get('record', 'F1'),
            play_hotkey=hotkeys.get('play', 'F2'),
            on_record=lambda: self.controller.toggle_recording(),
            on_play=lambda: self.controller.toggle_playback(),
            on_clear=lambda: self.controller.clear_recording(),
            on_save=lambda: self.controller.save_recording(),
            on_load=lambda: self.controller.load_recording()
        )
        self.control_widget.pack(fill="x", pady=(0, 5))
        
        # Settings Widget
        self.settings_widget = SettingsWidget(left_panel)
        self.settings_widget.pack(fill="x", pady=(0, 5))
        
        # Hotkey Widget
        self.hotkey_widget = HotkeyWidget(
            left_panel,
            hotkeys=hotkeys,
            on_capture=lambda ht: self.controller.capture_hotkey(ht)
        )
        self.hotkey_widget.pack(fill="x")
        
        # Right Panel
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="left", fill="both", expand=True, padx=(2, 5))
        
        # Status Widget
        self.status_widget = StatusWidget(right_panel)
        self.status_widget.pack(fill="x", pady=(0, 5))
        
        # Event Log Widget
        self.event_log_widget = EventLogWidget(right_panel)
        self.event_log_widget.pack(fill="both", expand=True)
        
        # Hotkey Info Label at bottom
        self.hotkey_info_widget = HotkeyInfoWidget(self.root, hotkeys)
        self.hotkey_info_widget.pack(pady=3)
    
    def _connect_controller(self):
        """Connect widgets to the controller."""
        self.controller.set_widgets(
            control_widget=self.control_widget,
            settings_widget=self.settings_widget,
            hotkey_widget=self.hotkey_widget,
            status_widget=self.status_widget,
            event_log_widget=self.event_log_widget,
            hotkey_info_widget=self.hotkey_info_widget
        )
    
    def on_closing(self):
        """Cleanup when closing the application."""
        self.controller.cleanup()
        self.root.destroy()
