"""Control widget - Record, Play, Clear, Save, Load buttons."""

import tkinter as tk
from typing import Callable, Optional

from utils.constants import Colors, Fonts


class ControlWidget(tk.LabelFrame):
    """Widget containing main control buttons."""
    
    def __init__(
        self,
        parent: tk.Widget,
        record_hotkey: str = "F1",
        play_hotkey: str = "F2",
        on_record: Optional[Callable[[], None]] = None,
        on_play: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        on_save: Optional[Callable[[], None]] = None,
        on_load: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, text="Controls", padx=8, pady=5)
        
        # Store callbacks
        self._on_record = on_record
        self._on_play = on_play
        self._on_clear = on_clear
        self._on_save = on_save
        self._on_load = on_load
        
        # Create buttons
        self._create_buttons(record_hotkey, play_hotkey)
    
    def _create_buttons(self, record_hotkey: str, play_hotkey: str):
        """Create all control buttons."""
        # Record Button
        self.record_btn = tk.Button(
            self,
            text=f"Record ({record_hotkey})",
            command=self._handle_record,
            bg=Colors.RECORD,
            fg=Colors.BUTTON_TEXT,
            font=Fonts.BUTTON,
            height=1
        )
        self.record_btn.pack(fill="x", padx=3, pady=2)
        
        # Play Button
        self.play_btn = tk.Button(
            self,
            text=f"Play ({play_hotkey})",
            command=self._handle_play,
            bg=Colors.PLAY,
            fg=Colors.BUTTON_TEXT,
            font=Fonts.BUTTON,
            height=1
        )
        self.play_btn.pack(fill="x", padx=3, pady=2)
        
        # Clear Button
        self.clear_btn = tk.Button(
            self,
            text="Clear",
            command=self._handle_clear,
            bg=Colors.CLEAR,
            fg=Colors.BUTTON_TEXT,
            font=Fonts.BUTTON,
            height=1
        )
        self.clear_btn.pack(fill="x", padx=3, pady=2)
        
        # Save/Load Frame
        saveload_frame = tk.Frame(self)
        saveload_frame.pack(fill="x", padx=3, pady=2)
        
        # Save Button
        self.save_btn = tk.Button(
            saveload_frame,
            text="Save",
            command=self._handle_save,
            bg=Colors.SAVE,
            fg=Colors.BUTTON_TEXT,
            font=Fonts.BUTTON,
            height=1
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Load Button
        self.load_btn = tk.Button(
            saveload_frame,
            text="Load",
            command=self._handle_load,
            bg=Colors.LOAD,
            fg=Colors.BUTTON_TEXT,
            font=Fonts.BUTTON,
            height=1
        )
        self.load_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
    
    # -------------------------------------------------------------------------
    # Public: Update button states
    # -------------------------------------------------------------------------
    
    def set_recording_state(self, is_recording: bool, hotkey: str):
        """Update record button to reflect recording state."""
        if is_recording:
            self.record_btn.config(
                text=f"Stop ({hotkey})",
                bg=Colors.RECORD_ACTIVE
            )
        else:
            self.record_btn.config(
                text=f"Record ({hotkey})",
                bg=Colors.RECORD
            )
    
    def set_playing_state(self, is_playing: bool, hotkey: str):
        """Update play button to reflect playing state."""
        if is_playing:
            self.play_btn.config(
                text=f"Stop ({hotkey})",
                bg=Colors.PLAY_ACTIVE
            )
        else:
            self.play_btn.config(
                text=f"Play ({hotkey})",
                bg=Colors.PLAY
            )
    
    def update_hotkeys(self, record_hotkey: str, play_hotkey: str):
        """Update button labels with new hotkey names."""
        current_record_text = self.record_btn.cget("text")
        current_play_text = self.play_btn.cget("text")
        
        # Preserve "Stop" vs "Record/Play" state
        if current_record_text.startswith("Stop"):
            self.record_btn.config(text=f"Stop ({record_hotkey})")
        else:
            self.record_btn.config(text=f"Record ({record_hotkey})")
        
        if current_play_text.startswith("Stop"):
            self.play_btn.config(text=f"Stop ({play_hotkey})")
        else:
            self.play_btn.config(text=f"Play ({play_hotkey})")
    
    # -------------------------------------------------------------------------
    # Private: Button handlers
    # -------------------------------------------------------------------------
    
    def _handle_record(self):
        if self._on_record:
            self._on_record()
    
    def _handle_play(self):
        if self._on_play:
            self._on_play()
    
    def _handle_clear(self):
        if self._on_clear:
            self._on_clear()
    
    def _handle_save(self):
        if self._on_save:
            self._on_save()
    
    def _handle_load(self):
        if self._on_load:
            self._on_load()
