"""Event log display widget."""

import tkinter as tk
from tkinter import scrolledtext
from typing import List

from utils.constants import Fonts


class EventLogWidget(tk.LabelFrame):
    """Widget for displaying recorded events."""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Recorded Events", padx=8, pady=5)
        
        self._text = scrolledtext.ScrolledText(
            self,
            height=10,
            font=Fonts.EVENT_LOG,
            wrap=tk.WORD
        )
        self._text.pack(fill="both", expand=True)
    
    def append(self, text: str):
        """Append text to the log and scroll to bottom."""
        self._text.insert(tk.END, text)
        self._text.see(tk.END)
    
    def clear(self):
        """Clear all text from the log."""
        self._text.delete(1.0, tk.END)
    
    def set_content(self, text: str):
        """Replace all content with new text."""
        self.clear()
        self._text.insert(tk.END, text)
        self._text.see(tk.END)
    
    def display_events(self, events: List[dict]):
        """Format and display a list of events."""
        self.clear()
        
        for event in events:
            timestamp = event['timestamp']
            event_type = event['type']
            
            if event_type == 'mouse_click':
                action = "Press" if event['pressed'] else "Release"
                line = f"[{timestamp:.2f}s] Mouse {action}: {event['button']} at ({event['x']}, {event['y']})\n"
            elif event_type == 'key_press':
                line = f"[{timestamp:.2f}s] Key Press: {event['key']}\n"
            elif event_type == 'key_release':
                line = f"[{timestamp:.2f}s] Key Release: {event['key']}\n"
            else:
                line = f"[{timestamp:.2f}s] Unknown: {event_type}\n"
            
            self._text.insert(tk.END, line)
        
        self._text.see(tk.END)
    
    @property
    def content(self) -> str:
        """Get all text content."""
        return self._text.get(1.0, tk.END)
