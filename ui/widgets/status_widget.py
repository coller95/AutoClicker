"""Status display widget."""

import tkinter as tk
from typing import Optional

from utils.constants import Colors, Fonts


class StatusWidget(tk.LabelFrame):
    """Widget for displaying application status."""
    
    def __init__(self, parent: tk.Widget, initial_text: str = "Ready"):
        super().__init__(parent, text="Status", padx=8, pady=5)
        
        self._label = tk.Label(
            self,
            text=initial_text,
            font=Fonts.STATUS,
            fg=Colors.STATUS_OK
        )
        self._label.pack()
    
    def set_status(self, message: str, color: str = Colors.STATUS_DEFAULT):
        """Update the status display.
        
        Args:
            message: Status message to display.
            color: Text color for the message.
        """
        self._label.config(text=message, fg=color)
    
    def set_ready(self):
        """Set status to ready state."""
        self.set_status("Ready", Colors.STATUS_OK)
    
    def set_error(self, message: str):
        """Set an error status."""
        self.set_status(message, Colors.STATUS_ERROR)
    
    def set_info(self, message: str):
        """Set an info status."""
        self.set_status(message, Colors.STATUS_INFO)
    
    @property
    def text(self) -> str:
        """Get current status text."""
        return self._label.cget("text")
