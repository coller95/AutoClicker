"""Hotkey information widget - displays current hotkey bindings."""

import tkinter as tk
from typing import Dict

from utils.constants import Colors, Fonts


class HotkeyInfoWidget(tk.Label):
    """Small label showing current hotkey bindings."""
    
    def __init__(self, parent: tk.Widget, hotkeys: Dict[str, str]):
        super().__init__(
            parent,
            text=self._format_info(hotkeys),
            font=Fonts.INFO,
            fg=Colors.INFO_TEXT
        )
    
    def update_info(self, hotkeys: Dict[str, str]):
        """Update the hotkey information display."""
        self.config(text=self._format_info(hotkeys))
    
    def _format_info(self, hotkeys: Dict[str, str]) -> str:
        """Format hotkeys into display string."""
        return (
            f"Hotkeys: {hotkeys.get('record', '?')}=Toggle Record | "
            f"{hotkeys.get('play', '?')}=Toggle Play/Stop | "
            f"{hotkeys.get('stop', '?')}=Force Stop | "
            f"{hotkeys.get('spam', '?')}=Toggle Spam Click"
        )
