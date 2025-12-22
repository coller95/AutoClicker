"""Hotkey configuration widget."""

import tkinter as tk
from typing import Callable, Optional, Dict

from utils.constants import Colors, Fonts


class HotkeyWidget(tk.LabelFrame):
    """Widget for configuring hotkeys."""
    
    def __init__(
        self,
        parent: tk.Widget,
        hotkeys: Dict[str, str],
        on_capture: Optional[Callable[[str], None]] = None
    ):
        """Initialize hotkey widget.
        
        Args:
            parent: Parent widget.
            hotkeys: Dictionary of hotkey names {'record': 'F1', 'play': 'F2', ...}
            on_capture: Callback when user wants to capture a hotkey.
        """
        super().__init__(parent, text="Hotkeys", padx=8, pady=5)
        
        self._on_capture = on_capture
        self._buttons: Dict[str, tk.Button] = {}
        
        self._create_controls(hotkeys)
    
    def _create_controls(self, hotkeys: Dict[str, str]):
        """Create hotkey configuration controls."""
        hotkey_configs = [
            ('record', 'Record:'),
            ('play', 'Play:'),
            ('stop', 'Stop:'),
            ('spam', 'Spam:'),
        ]
        
        for row, (key, label) in enumerate(hotkey_configs):
            tk.Label(self, text=label, font=Fonts.LABEL).grid(
                row=row, column=0, sticky="w", pady=2
            )
            
            btn = tk.Button(
                self,
                text=hotkeys.get(key, '?'),
                command=lambda k=key: self._handle_capture(k),
                width=10,
                font=Fonts.HOTKEY_BUTTON
            )
            btn.grid(row=row, column=1, sticky="ew", pady=2, padx=(5, 0))
            self._buttons[key] = btn
        
        self.columnconfigure(1, weight=1)
    
    # -------------------------------------------------------------------------
    # Public: Update hotkey display
    # -------------------------------------------------------------------------
    
    def set_capturing(self, hotkey_type: str):
        """Set a hotkey button to capturing mode."""
        if hotkey_type in self._buttons:
            self._buttons[hotkey_type].config(
                text="Press key...",
                bg=Colors.HOTKEY_CAPTURE
            )
    
    def set_hotkey(self, hotkey_type: str, key_name: str):
        """Update a hotkey button with the captured key."""
        if hotkey_type in self._buttons:
            self._buttons[hotkey_type].config(
                text=key_name,
                bg=Colors.HOTKEY_DEFAULT
            )
    
    def update_all(self, hotkeys: Dict[str, str]):
        """Update all hotkey buttons."""
        for key, name in hotkeys.items():
            if key in self._buttons:
                self._buttons[key].config(text=name, bg=Colors.HOTKEY_DEFAULT)
    
    # -------------------------------------------------------------------------
    # Private: Event handlers
    # -------------------------------------------------------------------------
    
    def _handle_capture(self, hotkey_type: str):
        """Handle capture button click."""
        if self._on_capture:
            self._on_capture(hotkey_type)
