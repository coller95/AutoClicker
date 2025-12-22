"""Application controller - coordinates all components."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from __version__ import __version__
from models.recorder import Recorder
from models.player import Player
from models.spam_clicker import SpamClicker
from models.hotkey_manager import HotkeyManager
from ui.banner import BannerManager
from utils.file_manager import FileManager
from utils.constants import Colors


class AppController:
    """Coordinates all application components and handles business logic."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Initialize core components
        self.recorder = Recorder()
        self.player = Player()
        self.spam_clicker = SpamClicker()
        self.hotkey_manager = HotkeyManager()
        self.banner_manager = BannerManager(root)
        
        # UI widgets (set later by main_window)
        self._control_widget = None
        self._settings_widget = None
        self._hotkey_widget = None
        self._status_widget = None
        self._event_log_widget = None
        self._hotkey_info_widget = None
        
        # Setup internal callbacks
        self._setup_callbacks()
    
    def set_widgets(
        self,
        control_widget=None,
        settings_widget=None,
        hotkey_widget=None,
        status_widget=None,
        event_log_widget=None,
        hotkey_info_widget=None
    ):
        """Set UI widget references."""
        if control_widget:
            self._control_widget = control_widget
        if settings_widget:
            self._settings_widget = settings_widget
        if hotkey_widget:
            self._hotkey_widget = hotkey_widget
        if status_widget:
            self._status_widget = status_widget
        if event_log_widget:
            self._event_log_widget = event_log_widget
        if hotkey_info_widget:
            self._hotkey_info_widget = hotkey_info_widget
    
    def _setup_callbacks(self):
        """Setup callbacks for all components."""
        # Recorder callbacks
        self.recorder.set_callbacks(
            on_event=self._on_event_recorded,
            on_status=self._update_status_threadsafe,
            on_live_input=self._on_live_input
        )
        
        # Player callbacks
        self.player.set_callbacks(
            on_status=self._update_status_threadsafe,
            on_complete=self._on_playback_complete,
            on_live_input=self._on_live_input,
            on_countdown=self._on_delay_countdown
        )
        
        # Spam clicker callbacks
        self.spam_clicker.set_callbacks(
            on_status=self._update_status_threadsafe
        )
        
        # Hotkey manager callbacks
        self.hotkey_manager.set_callbacks(
            on_record=lambda: self.root.after(0, self.toggle_recording),
            on_play=lambda: self.root.after(0, self.toggle_playback),
            on_stop=lambda: self.root.after(0, self.force_stop),
            on_spam=lambda: self.root.after(0, self.toggle_spam_click),
            on_hotkey_captured=self._on_hotkey_captured,
            on_status=self._update_status_threadsafe
        )
    
    def start(self):
        """Start the controller (setup hotkey listener)."""
        self.root.after(100, self.hotkey_manager.setup_listener)
    
    # -------------------------------------------------------------------------
    # Recording
    # -------------------------------------------------------------------------
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if self.recorder.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording events."""
        if self.spam_clicker.is_active():
            self._update_status("Stop spam clicking first!", Colors.STATUS_ERROR)
            return
        
        if self.player.is_playing:
            self._update_status("Stop playback first!", Colors.STATUS_ERROR)
            return
        
        # Update ignored keys before recording
        self.recorder.set_ignored_keys(self.hotkey_manager.get_ignored_keys())
        
        if self.recorder.start():
            self._set_window_title(f"🔴 RECORDING - AutoClicker v{__version__}")
            
            stop_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_stop)
            record_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record)
            
            self.banner_manager.show_banner(
                "● RECORDING",
                Colors.BANNER_RECORDING,
                f"Press {stop_key} or {record_key} to stop"
            )
            
            if self._control_widget:
                self._control_widget.set_recording_state(True, record_key)
            
            if self._event_log_widget:
                self._event_log_widget.clear()
    
    def stop_recording(self):
        """Stop recording events."""
        self.recorder.stop()
        self._set_window_title(f"AutoClicker v{__version__}")
        self.banner_manager.hide_banner()
        
        if self._control_widget:
            record_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record)
            self._control_widget.set_recording_state(False, record_key)
    
    # -------------------------------------------------------------------------
    # Playback
    # -------------------------------------------------------------------------
    
    def toggle_playback(self):
        """Toggle playback on/off."""
        if self.player.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start playing back recorded events."""
        if self.spam_clicker.is_active():
            self._update_status("Stop spam clicking first!", Colors.STATUS_ERROR)
            return
        
        if self.recorder.is_recording:
            self._update_status("Stop recording first!", Colors.STATUS_ERROR)
            return
        
        events = self.recorder.get_events()
        if not events:
            self._update_status("No events to play!", Colors.STATUS_ERROR)
            return
        
        # Get settings
        loop_count = self._settings_widget.loop_count if self._settings_widget else 1
        loop_delay = self._settings_widget.loop_delay if self._settings_widget else 0.0
        playback_speed = self._settings_widget.playback_speed if self._settings_widget else 1.0
        
        if self.player.start(events, loop_count, loop_delay, playback_speed):
            self._set_window_title(f"▶️ PLAYING - AutoClicker v{__version__}")
            
            stop_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_stop)
            loop_info = f"Loop: {loop_count}x" if loop_count > 0 else "Loop: ∞"
            speed_info = f" | Speed: {playback_speed}x" if playback_speed != 1.0 else ""
            
            self.banner_manager.show_banner(
                "▶ PLAYING",
                Colors.BANNER_PLAYING,
                f"{loop_info}{speed_info} | Press {stop_key} to stop"
            )
            
            if self._control_widget:
                play_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)
                self._control_widget.set_playing_state(True, play_key)
    
    def stop_playback(self):
        """Stop playback."""
        if self.player.stop():
            self._set_window_title(f"AutoClicker v{__version__}")
            self.banner_manager.hide_banner()
            
            if self._control_widget:
                play_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)
                self._control_widget.set_playing_state(False, play_key)
    
    # -------------------------------------------------------------------------
    # Spam Click
    # -------------------------------------------------------------------------
    
    def toggle_spam_click(self):
        """Toggle spam clicking on/off."""
        if self.spam_clicker.is_active():
            self.stop_spam_click()
        else:
            self.start_spam_click()
    
    def start_spam_click(self):
        """Start spam clicking."""
        if self.recorder.is_recording:
            self._update_status("Cannot spam click while recording!", Colors.STATUS_ERROR)
            return
        
        if self.player.is_playing:
            self._update_status("Cannot spam click while playing!", Colors.STATUS_ERROR)
            return
        
        if self.spam_clicker.start_spam_click():
            self._set_window_title(f"⚡ SPAM CLICKING - AutoClicker v{__version__}")
            
            stop_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_spam)
            self.banner_manager.show_banner(
                "⚡ SPAM CLICKING",
                Colors.BANNER_SPAM,
                f"Press {stop_key} to stop"
            )
    
    def stop_spam_click(self):
        """Stop spam clicking."""
        if self.spam_clicker.stop_spam_click():
            self._set_window_title(f"AutoClicker v{__version__}")
            self.banner_manager.hide_banner()
    
    # -------------------------------------------------------------------------
    # Other Actions
    # -------------------------------------------------------------------------
    
    def force_stop(self):
        """Force stop all activities."""
        if self.recorder.is_recording:
            self.stop_recording()
        elif self.player.is_playing:
            self.stop_playback()
        elif self.spam_clicker.is_active():
            self.stop_spam_click()
    
    def clear_recording(self):
        """Clear recorded events."""
        self.recorder.clear()
        if self._event_log_widget:
            self._event_log_widget.clear()
    
    def save_recording(self):
        """Save recorded events to file."""
        if self.recorder.is_recording:
            messagebox.showwarning("Recording Active", "Please stop recording before saving!")
            return
        
        if self.player.is_playing:
            messagebox.showwarning("Playback Active", "Please stop playback before saving!")
            return
        
        events = self.recorder.get_events()
        config_data = {
            "loops": self._settings_widget.loop_count if self._settings_widget else 1,
            "delay": self._settings_widget.loop_delay if self._settings_widget else 0.0,
            "speed": self._settings_widget.playback_speed if self._settings_widget else 1.0,
            "hotkeys": self.hotkey_manager.get_hotkeys()
        }
        
        success, filepath, message = FileManager.save_recording(events, config_data)
        if success:
            self._update_status(message, Colors.STATUS_OK)
        else:
            self._update_status(message, Colors.STATUS_ERROR)
    
    def load_recording(self):
        """Load recorded events from file."""
        if self.recorder.is_recording:
            messagebox.showwarning("Recording Active", "Please stop recording before loading!")
            return
        
        if self.player.is_playing:
            messagebox.showwarning("Playback Active", "Please stop playback before loading!")
            return
        
        success, events, config, message = FileManager.load_recording()
        
        if success and events:
            self.recorder.set_events(events)
            
            if self._event_log_widget:
                self._event_log_widget.display_events(events)
            
            # Load configuration
            if config:
                if self._settings_widget:
                    self._settings_widget.set_config(config)
                
                if 'hotkeys' in config:
                    self.hotkey_manager.set_hotkeys(config['hotkeys'])
                    hotkeys = self.hotkey_manager.get_hotkeys()
                    
                    if self._hotkey_widget:
                        self._hotkey_widget.update_all(hotkeys)
                    
                    if self._control_widget:
                        self._control_widget.update_hotkeys(
                            hotkeys.get('record', 'F1'),
                            hotkeys.get('play', 'F2')
                        )
                    
                    if self._hotkey_info_widget:
                        self._hotkey_info_widget.update_info(hotkeys)
                    
                    self.recorder.set_ignored_keys(self.hotkey_manager.get_ignored_keys())
            
            self._update_status(message, Colors.STATUS_OK)
        else:
            self._update_status(message, Colors.STATUS_ERROR)
    
    def capture_hotkey(self, hotkey_type: str):
        """Start capturing a new hotkey."""
        self.hotkey_manager.start_capture(hotkey_type)
        
        if self._hotkey_widget:
            self._hotkey_widget.set_capturing(hotkey_type)
    
    def get_hotkeys(self) -> dict:
        """Get current hotkey configuration."""
        return self.hotkey_manager.get_hotkeys()
    
    def cleanup(self):
        """Cleanup when closing the application."""
        self.recorder.is_recording = False
        self.player.is_playing = False
        self.spam_clicker.is_spam_clicking = False
        
        self.banner_manager.cleanup()
        self.hotkey_manager.stop_listener()
    
    # -------------------------------------------------------------------------
    # Private: Callbacks
    # -------------------------------------------------------------------------
    
    def _on_event_recorded(self, log_text: str):
        """Callback when an event is recorded."""
        if self._event_log_widget:
            self._event_log_widget.append(log_text)
    
    def _update_status_threadsafe(self, message: str, color: str = Colors.STATUS_DEFAULT):
        """Thread-safe status update."""
        self.root.after(0, self._update_status, message, color)
    
    def _update_status(self, message: str, color: str = Colors.STATUS_DEFAULT):
        """Update status display."""
        if self._status_widget:
            self._status_widget.set_status(message, color)
        
        # Show in banner if active
        if self.banner_manager.banner_windows:
            self.banner_manager.update_status(f"⚠ {message}", self._get_default_banner_status(), duration=2500)
        elif color == Colors.STATUS_ERROR:
            self.banner_manager.show_status_message(f"⚠ {message}", Colors.BANNER_WARNING, duration=2000)
    
    def _get_default_banner_status(self) -> Optional[str]:
        """Get default banner status based on current state."""
        if self.recorder.is_recording:
            stop_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_stop)
            record_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record)
            return f"Press {stop_key} or {record_key} to stop"
        elif self.player.is_playing:
            stop_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_stop)
            loop_count = self._settings_widget.loop_count if self._settings_widget else 1
            playback_speed = self._settings_widget.playback_speed if self._settings_widget else 1.0
            loop_info = f"Loop: {loop_count}x" if loop_count > 0 else "Loop: ∞"
            speed_info = f" | Speed: {playback_speed}x" if playback_speed != 1.0 else ""
            return f"{loop_info}{speed_info} | Press {stop_key} to stop"
        elif self.spam_clicker.is_active():
            stop_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_spam)
            return f"Press {stop_key} to stop"
        return None
    
    def _on_live_input(self, input_type: str, input_text: str):
        """Callback when a live input event occurs."""
        self.root.after(0, self._update_live_input_display, input_type, input_text)
    
    def _update_live_input_display(self, input_type: str, input_text: str):
        """Update the live input display."""
        self.banner_manager.update_live_input(input_type, input_text)
        
        if self._status_widget:
            if self.recorder.is_recording:
                event_count = self.recorder.event_count
                self._status_widget.set_status(
                    f"Recording: {event_count} events | Last: {input_text}",
                    Colors.STATUS_ERROR
                )
            elif self.player.is_playing:
                self._status_widget.set_status(
                    f"Playing | Last: {input_text}",
                    Colors.STATUS_INFO
                )
    
    def _on_delay_countdown(self, remaining_seconds: float):
        """Callback when countdown timer updates."""
        self.root.after(0, self.banner_manager.update_countdown, remaining_seconds)
    
    def _on_playback_complete(self):
        """Callback when playback completes."""
        self.root.after(0, self._handle_playback_complete)
    
    def _handle_playback_complete(self):
        """Handle playback completion."""
        self._set_window_title(f"AutoClicker v{__version__}")
        self.banner_manager.hide_banner()
        
        if self._control_widget:
            play_key = self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)
            self._control_widget.set_playing_state(False, play_key)
    
    def _on_hotkey_captured(self, hotkey_type: str, key):
        """Callback when a hotkey is captured."""
        key_name = self.hotkey_manager.get_key_name(key)
        
        if self._hotkey_widget:
            self._hotkey_widget.set_hotkey(hotkey_type, key_name)
        
        if self._control_widget:
            hotkeys = self.hotkey_manager.get_hotkeys()
            self._control_widget.update_hotkeys(
                hotkeys.get('record', 'F1'),
                hotkeys.get('play', 'F2')
            )
        
        if self._hotkey_info_widget:
            self._hotkey_info_widget.update_info(self.hotkey_manager.get_hotkeys())
        
        self.recorder.set_ignored_keys(self.hotkey_manager.get_ignored_keys())
    
    def _set_window_title(self, title: str):
        """Set the window title."""
        self.root.title(title)
