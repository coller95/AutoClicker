"""Settings widget - Loop count, delay, and playback speed."""

import tkinter as tk
from typing import Optional

from utils.constants import Fonts, Defaults


class SettingsWidget(tk.LabelFrame):
    """Widget containing playback settings controls."""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Settings", padx=8, pady=5)
        
        self._create_controls()
    
    def _create_controls(self):
        """Create all settings controls."""
        # Loop Count
        tk.Label(self, text="Loops:", font=Fonts.LABEL).grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.loop_spinbox = tk.Spinbox(
            self,
            from_=Defaults.LOOP_MIN,
            to=Defaults.LOOP_MAX,
            width=8,
            font=Fonts.LABEL
        )
        self.loop_spinbox.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))
        self.loop_spinbox.delete(0, "end")
        self.loop_spinbox.insert(0, str(Defaults.LOOP_COUNT))
        tk.Label(self, text="(0=∞)", fg="gray", font=Fonts.LABEL_SMALL).grid(
            row=0, column=2, sticky="w", padx=3
        )
        
        # Delay Between Loops
        tk.Label(self, text="Delay:", font=Fonts.LABEL).grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.delay_spinbox = tk.Spinbox(
            self,
            from_=Defaults.DELAY_MIN,
            to=Defaults.DELAY_MAX,
            increment=Defaults.DELAY_INCREMENT,
            width=8,
            format="%.1f",
            font=Fonts.LABEL
        )
        self.delay_spinbox.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))
        self.delay_spinbox.delete(0, "end")
        self.delay_spinbox.insert(0, str(Defaults.LOOP_DELAY))
        tk.Label(self, text="(sec)", fg="gray", font=Fonts.LABEL_SMALL).grid(
            row=1, column=2, sticky="w", padx=3
        )
        
        # Playback Speed
        tk.Label(self, text="Speed:", font=Fonts.LABEL).grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.speed_spinbox = tk.Spinbox(
            self,
            from_=Defaults.SPEED_MIN,
            to=Defaults.SPEED_MAX,
            increment=Defaults.SPEED_INCREMENT,
            width=8,
            format="%.1f",
            font=Fonts.LABEL
        )
        self.speed_spinbox.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))
        self.speed_spinbox.delete(0, "end")
        self.speed_spinbox.insert(0, str(Defaults.PLAYBACK_SPEED))
        tk.Label(self, text="(x)", fg="gray", font=Fonts.LABEL_SMALL).grid(
            row=2, column=2, sticky="w", padx=3
        )
        
        # Configure column weight
        self.columnconfigure(1, weight=1)
    
    # -------------------------------------------------------------------------
    # Public: Get/Set values
    # -------------------------------------------------------------------------
    
    @property
    def loop_count(self) -> int:
        """Get the loop count value."""
        return int(self.loop_spinbox.get())
    
    @loop_count.setter
    def loop_count(self, value: int):
        """Set the loop count value."""
        self.loop_spinbox.delete(0, "end")
        self.loop_spinbox.insert(0, str(value))
    
    @property
    def loop_delay(self) -> float:
        """Get the loop delay value."""
        return float(self.delay_spinbox.get())
    
    @loop_delay.setter
    def loop_delay(self, value: float):
        """Set the loop delay value."""
        self.delay_spinbox.delete(0, "end")
        self.delay_spinbox.insert(0, str(value))
    
    @property
    def playback_speed(self) -> float:
        """Get the playback speed value."""
        return float(self.speed_spinbox.get())
    
    @playback_speed.setter
    def playback_speed(self, value: float):
        """Set the playback speed value."""
        self.speed_spinbox.delete(0, "end")
        self.speed_spinbox.insert(0, str(value))
    
    def get_config(self) -> dict:
        """Get all settings as a dictionary."""
        return {
            'loops': self.loop_count,
            'delay': self.loop_delay,
            'speed': self.playback_speed
        }
    
    def set_config(self, config: dict):
        """Set all settings from a dictionary."""
        if 'loops' in config:
            self.loop_count = config['loops']
        if 'delay' in config:
            self.loop_delay = config['delay']
        if 'speed' in config:
            self.playback_speed = config['speed']
