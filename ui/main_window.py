"""Main window UI for AutoClicker application."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
from __version__ import __version__
from models.event_recorder import EventRecorder
from models.spam_clicker import SpamClicker
from models.hotkey_manager import HotkeyManager
from ui.banner import BannerManager
from utils.file_manager import FileManager


class MainWindow:
    """Main application window for AutoClicker."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"AutoClicker v{__version__}")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        self.root.minsize(750, 450)
        
        # Set window icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"))
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass  # Icon file may not be supported on this platform
        
        # Initialize components
        self.event_recorder = EventRecorder()
        self.spam_clicker = SpamClicker()
        self.hotkey_manager = HotkeyManager()
        self.banner_manager = BannerManager(root)
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Setup UI
        self.setup_ui()
        
        # Setup hotkeys - delay to avoid race condition with mainloop
        self.root.after(100, self._delayed_hotkey_setup)
    
    def _delayed_hotkey_setup(self):
        """Setup hotkey listener after mainloop has started."""
        self.hotkey_manager.setup_listener()
    
    def _setup_callbacks(self):
        """Setup callbacks for all components."""
        # Event recorder callbacks
        self.event_recorder.set_callbacks(
            on_event=self._on_event_recorded,
            on_status=self._update_status_threadsafe,
            on_playback_complete=self._on_playback_complete
        )
        
        # Spam clicker callbacks
        self.spam_clicker.set_callbacks(
            on_status=self._update_status_threadsafe
        )
        
        # Hotkey manager callbacks - wrap in thread-safe calls
        self.hotkey_manager.set_callbacks(
            on_record=lambda: self.root.after(0, self.toggle_recording),
            on_play=lambda: self.root.after(0, self.toggle_playback),
            on_stop=lambda: self.root.after(0, self.force_stop),
            on_spam=lambda: self.root.after(0, self.toggle_spam_click),
            on_hotkey_captured=self._on_hotkey_captured,
            on_status=self._update_status_threadsafe
        )
        
        # Update ignored keys for event recorder
        self.event_recorder.set_ignored_keys(self.hotkey_manager.get_ignored_keys())
    
    def _on_event_recorded(self, log_text):
        """Callback when an event is recorded."""
        self.event_log.insert(tk.END, log_text)
        self.event_log.see(tk.END)
    
    def _update_status_threadsafe(self, message, color="black"):
        """Thread-safe status update."""
        self.root.after(0, self.update_status, message, color)
    
    def _on_playback_complete(self):
        """Callback when playback completes."""
        self.root.after(0, lambda: self.root.title(f"AutoClicker v{__version__}"))
        self.root.after(0, self.banner_manager.hide_banner)
        self.root.after(0, lambda: self.play_btn.config(
            text=f"Play ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)})", 
            bg="#2196F3"
        ))
    
    def _on_hotkey_captured(self, hotkey_type, key):
        """Callback when a hotkey is captured."""
        key_name = self.hotkey_manager.get_key_name(key)
        
        if hotkey_type == 'record':
            self.record_hotkey_btn.config(text=key_name, bg="SystemButtonFace")
            self.record_btn.config(text=f"Record ({key_name})")
        elif hotkey_type == 'play':
            self.play_hotkey_btn.config(text=key_name, bg="SystemButtonFace")
            self.play_btn.config(text=f"Play ({key_name})")
        elif hotkey_type == 'stop':
            self.stop_hotkey_btn.config(text=key_name, bg="SystemButtonFace")
        elif hotkey_type == 'spam':
            self.spam_hotkey_btn.config(text=key_name, bg="SystemButtonFace")
        
        self.info_label.config(text=self.get_hotkey_info())
        self.event_recorder.set_ignored_keys(self.hotkey_manager.get_ignored_keys())
    
    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title_label = tk.Label(self.root, text="AutoClicker with Recording", 
                              font=("Arial", 12, "bold"))
        title_label.pack(pady=5)
        
        # Main container with left and right panels
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left Panel - Controls and Settings
        left_panel = tk.Frame(main_container, width=280)
        left_panel.pack(side="left", fill="both", padx=(5,2))
        left_panel.pack_propagate(False)
        
        # Control Frame
        self._setup_control_frame(left_panel)
        
        # Settings Frame
        self._setup_settings_frame(left_panel)
        
        # Hotkey Configuration Frame
        self._setup_hotkey_frame(left_panel)
        
        # Right Panel - Status and Event Log
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="left", fill="both", expand=True, padx=(2,5))
        
        # Status Frame
        self._setup_status_frame(right_panel)
        
        # Event Log
        self._setup_event_log(right_panel)
        
        # Info Label at bottom
        self.info_label = tk.Label(self.root, 
                             text=self.get_hotkey_info(),
                             font=("Arial", 7), fg="gray")
        self.info_label.pack(pady=3)
    
    def _setup_control_frame(self, parent):
        """Setup the control buttons frame."""
        control_frame = tk.LabelFrame(parent, text="Controls", padx=8, pady=5)
        control_frame.pack(fill="x", pady=(0,5))
        
        # Record Button
        self.record_btn = tk.Button(
            control_frame, 
            text=f"Record ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record)})", 
            command=self.toggle_recording,
            bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
            height=1
        )
        self.record_btn.pack(fill="x", padx=3, pady=2)
        
        # Play/Stop Toggle Button
        self.play_btn = tk.Button(
            control_frame, 
            text=f"Play ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)})", 
            command=self.toggle_playback,
            bg="#2196F3", fg="white", font=("Arial", 9, "bold"),
            height=1
        )
        self.play_btn.pack(fill="x", padx=3, pady=2)
        
        # Clear Button
        clear_btn = tk.Button(
            control_frame, 
            text="Clear", 
            command=self.clear_recording,
            bg="#FF9800", fg="white", font=("Arial", 9, "bold"),
            height=1
        )
        clear_btn.pack(fill="x", padx=3, pady=2)
        
        # Save/Load Frame
        saveload_frame = tk.Frame(control_frame)
        saveload_frame.pack(fill="x", padx=3, pady=2)
        
        # Save Button
        save_btn = tk.Button(
            saveload_frame, 
            text="Save", 
            command=self.save_recording,
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
            height=1
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=(0,2))
        
        # Load Button
        load_btn = tk.Button(
            saveload_frame, 
            text="Load", 
            command=self.load_recording,
            bg="#009688", fg="white", font=("Arial", 9, "bold"),
            height=1
        )
        load_btn.pack(side="left", fill="x", expand=True, padx=(2,0))
    
    def _setup_settings_frame(self, parent):
        """Setup the settings frame."""
        settings_frame = tk.LabelFrame(parent, text="Settings", padx=8, pady=5)
        settings_frame.pack(fill="x", pady=(0,5))
        
        # Loop Count
        tk.Label(settings_frame, text="Loops:", font=("Arial", 8)).grid(row=0, column=0, sticky="w", pady=2)
        self.loop_spinbox = tk.Spinbox(settings_frame, from_=0, to=100, width=8, font=("Arial", 8))
        self.loop_spinbox.grid(row=0, column=1, sticky="ew", pady=2, padx=(5,0))
        self.loop_spinbox.delete(0, "end")
        self.loop_spinbox.insert(0, "0")
        tk.Label(settings_frame, text="(0=∞)", fg="gray", font=("Arial", 7)).grid(row=0, column=2, sticky="w", padx=3)
        
        # Delay Between Loops
        tk.Label(settings_frame, text="Delay:", font=("Arial", 8)).grid(row=1, column=0, sticky="w", pady=2)
        self.delay_spinbox = tk.Spinbox(settings_frame, from_=0, to=60, increment=0.5, width=8, format="%.1f", font=("Arial", 8))
        self.delay_spinbox.grid(row=1, column=1, sticky="ew", pady=2, padx=(5,0))
        self.delay_spinbox.delete(0, "end")
        self.delay_spinbox.insert(0, "0.0")
        tk.Label(settings_frame, text="(sec)", fg="gray", font=("Arial", 7)).grid(row=1, column=2, sticky="w", padx=3)
        
        # Playback Speed
        tk.Label(settings_frame, text="Speed:", font=("Arial", 8)).grid(row=2, column=0, sticky="w", pady=2)
        self.speed_spinbox = tk.Spinbox(settings_frame, from_=0.1, to=10.0, increment=0.1, width=8, format="%.1f", font=("Arial", 8))
        self.speed_spinbox.grid(row=2, column=1, sticky="ew", pady=2, padx=(5,0))
        self.speed_spinbox.delete(0, "end")
        self.speed_spinbox.insert(0, "1.0")
        tk.Label(settings_frame, text="(x)", fg="gray", font=("Arial", 7)).grid(row=2, column=2, sticky="w", padx=3)
        
        settings_frame.columnconfigure(1, weight=1)
    
    def _setup_hotkey_frame(self, parent):
        """Setup the hotkey configuration frame."""
        hotkey_frame = tk.LabelFrame(parent, text="Hotkeys", padx=8, pady=5)
        hotkey_frame.pack(fill="x")
        
        tk.Label(hotkey_frame, text="Record:", font=("Arial", 8)).grid(row=0, column=0, sticky="w", pady=2)
        self.record_hotkey_btn = tk.Button(
            hotkey_frame, 
            text=self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record),
            command=lambda: self.capture_hotkey('record'),
            width=10, font=("Arial", 8)
        )
        self.record_hotkey_btn.grid(row=0, column=1, sticky="ew", pady=2, padx=(5,0))
        
        tk.Label(hotkey_frame, text="Play:", font=("Arial", 8)).grid(row=1, column=0, sticky="w", pady=2)
        self.play_hotkey_btn = tk.Button(
            hotkey_frame, 
            text=self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play),
            command=lambda: self.capture_hotkey('play'),
            width=10, font=("Arial", 8)
        )
        self.play_hotkey_btn.grid(row=1, column=1, sticky="ew", pady=2, padx=(5,0))
        
        tk.Label(hotkey_frame, text="Stop:", font=("Arial", 8)).grid(row=2, column=0, sticky="w", pady=2)
        self.stop_hotkey_btn = tk.Button(
            hotkey_frame, 
            text=self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_stop),
            command=lambda: self.capture_hotkey('stop'),
            width=10, font=("Arial", 8)
        )
        self.stop_hotkey_btn.grid(row=2, column=1, sticky="ew", pady=2, padx=(5,0))
        
        tk.Label(hotkey_frame, text="Spam:", font=("Arial", 8)).grid(row=3, column=0, sticky="w", pady=2)
        self.spam_hotkey_btn = tk.Button(
            hotkey_frame, 
            text=self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_spam),
            command=lambda: self.capture_hotkey('spam'),
            width=10, font=("Arial", 8)
        )
        self.spam_hotkey_btn.grid(row=3, column=1, sticky="ew", pady=2, padx=(5,0))
        
        hotkey_frame.columnconfigure(1, weight=1)
    
    def _setup_status_frame(self, parent):
        """Setup the status display frame."""
        status_frame = tk.LabelFrame(parent, text="Status", padx=8, pady=5)
        status_frame.pack(fill="x", pady=(0,5))
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                     font=("Arial", 9), fg="green")
        self.status_label.pack()
    
    def _setup_event_log(self, parent):
        """Setup the event log display."""
        log_frame = tk.LabelFrame(parent, text="Recorded Events", padx=8, pady=5)
        log_frame.pack(fill="both", expand=True)
        
        self.event_log = scrolledtext.ScrolledText(log_frame, height=10, 
                                                    font=("Courier", 8), wrap=tk.WORD)
        self.event_log.pack(fill="both", expand=True)
    
    def get_hotkey_info(self):
        """Get hotkey information string."""
        hotkeys = self.hotkey_manager.get_hotkeys()
        return f"Hotkeys: {hotkeys['record']}=Toggle Record | {hotkeys['play']}=Toggle Play/Stop | {hotkeys['stop']}=Force Stop | {hotkeys['spam']}=Toggle Spam Click"
    
    def capture_hotkey(self, hotkey_type):
        """Start capturing a new hotkey."""
        self.hotkey_manager.start_capture(hotkey_type)
        
        if hotkey_type == 'record':
            self.record_hotkey_btn.config(text="Press key...", bg="yellow")
        elif hotkey_type == 'play':
            self.play_hotkey_btn.config(text="Press key...", bg="yellow")
        elif hotkey_type == 'stop':
            self.stop_hotkey_btn.config(text="Press key...", bg="yellow")
        elif hotkey_type == 'spam':
            self.spam_hotkey_btn.config(text="Press key...", bg="yellow")
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if self.event_recorder.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording events."""
        if self.spam_clicker.is_active():
            self.update_status("Stop spam clicking first!", "red")
            return
        
        if self.event_recorder.start_recording():
            self.root.title(f"🔴 RECORDING - AutoClicker v{__version__}")
            self.banner_manager.show_banner("● RECORDING", "#f44336")
            self.record_btn.config(
                text=f"Stop ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record)})", 
                bg="#f44336"
            )
            self.event_log.delete(1.0, tk.END)
    
    def stop_recording(self):
        """Stop recording events."""
        self.event_recorder.stop_recording()
        self.root.title(f"AutoClicker v{__version__}")
        self.banner_manager.hide_banner()
        self.record_btn.config(
            text=f"Record ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_record)})", 
            bg="#4CAF50"
        )
    
    def toggle_playback(self):
        """Toggle playback on/off."""
        if self.event_recorder.is_playing:
            self.stop_playback()
        else:
            self.play_recording()
    
    def play_recording(self):
        """Start playing back recorded events."""
        if self.spam_clicker.is_active():
            self.update_status("Stop spam clicking first!", "red")
            return
        
        loop_count = int(self.loop_spinbox.get())
        loop_delay = float(self.delay_spinbox.get())
        playback_speed = float(self.speed_spinbox.get())
        
        if self.event_recorder.start_playback(loop_count, loop_delay, playback_speed):
            self.root.title(f"▶️ PLAYING - AutoClicker v{__version__}")
            self.banner_manager.show_banner("▶ PLAYING", "#2196F3")
            self.play_btn.config(
                text=f"Stop ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)})", 
                bg="#f44336"
            )
    
    def stop_playback(self):
        """Stop playback."""
        if self.event_recorder.stop_playback():
            self.root.title(f"AutoClicker v{__version__}")
            self.banner_manager.hide_banner()
            self.play_btn.config(
                text=f"Play ({self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_play)})", 
                bg="#2196F3"
            )
    
    def force_stop(self):
        """Force stop all activities."""
        if self.event_recorder.is_playing:
            self.stop_playback()
        elif self.spam_clicker.is_active():
            self.stop_spam_click()
    
    def clear_recording(self):
        """Clear recorded events."""
        self.event_recorder.clear_recording()
        self.event_log.delete(1.0, tk.END)
    
    def save_recording(self):
        """Save recorded events to file."""
        if self.event_recorder.is_recording:
            messagebox.showwarning("Recording Active", "Please stop recording before saving!")
            return
        
        if self.event_recorder.is_playing:
            messagebox.showwarning("Playback Active", "Please stop playback before saving!")
            return
        
        events = self.event_recorder.get_events()
        config_data = {
            "loops": int(self.loop_spinbox.get()),
            "delay": float(self.delay_spinbox.get()),
            "speed": float(self.speed_spinbox.get()),
            "hotkeys": self.hotkey_manager.get_hotkeys()
        }
        
        success, filepath, message = FileManager.save_recording(events, config_data)
        if success:
            self.update_status(message, "green")
        else:
            self.update_status(message, "red")
    
    def load_recording(self):
        """Load recorded events from file."""
        if self.event_recorder.is_recording:
            messagebox.showwarning("Recording Active", "Please stop recording before loading!")
            return
        
        if self.event_recorder.is_playing:
            messagebox.showwarning("Playback Active", "Please stop playback before loading!")
            return
        
        success, events, config, message = FileManager.load_recording()
        
        if success:
            self.event_recorder.set_events(events)
            self.event_log.delete(1.0, tk.END)
            
            # Display loaded events
            formatted_text = FileManager.format_events_for_display(events)
            self.event_log.insert(tk.END, formatted_text)
            self.event_log.see(tk.END)
            
            # Load configuration if available
            if config:
                if 'loops' in config:
                    self.loop_spinbox.delete(0, "end")
                    self.loop_spinbox.insert(0, str(config['loops']))
                if 'delay' in config:
                    self.delay_spinbox.delete(0, "end")
                    self.delay_spinbox.insert(0, str(config['delay']))
                if 'speed' in config:
                    self.speed_spinbox.delete(0, "end")
                    self.speed_spinbox.insert(0, str(config['speed']))
                if 'hotkeys' in config:
                    self.hotkey_manager.set_hotkeys(config['hotkeys'])
                    # Update button labels
                    hotkeys = self.hotkey_manager.get_hotkeys()
                    self.record_hotkey_btn.config(text=hotkeys['record'])
                    self.play_hotkey_btn.config(text=hotkeys['play'])
                    self.stop_hotkey_btn.config(text=hotkeys['stop'])
                    self.spam_hotkey_btn.config(text=hotkeys['spam'])
                    self.record_btn.config(text=f"Record ({hotkeys['record']})")
                    self.play_btn.config(text=f"Play ({hotkeys['play']})")
                    self.info_label.config(text=self.get_hotkey_info())
                    self.event_recorder.set_ignored_keys(self.hotkey_manager.get_ignored_keys())
            
            self.update_status(message, "green")
        else:
            self.update_status(message, "red")
    
    def toggle_spam_click(self):
        """Toggle spam clicking on/off."""
        if self.spam_clicker.is_active():
            self.stop_spam_click()
        else:
            self.start_spam_click()
    
    def start_spam_click(self):
        """Start spam clicking."""
        if self.event_recorder.is_recording:
            self.update_status("Cannot spam click while recording!", "red")
            return
        
        if self.event_recorder.is_playing:
            self.update_status("Cannot spam click while playing!", "red")
            return
        
        if self.spam_clicker.start_spam_click():
            self.root.title(f"⚡ SPAM CLICKING - AutoClicker v{__version__}")
            self.banner_manager.show_banner("⚡ SPAM CLICKING", "#FF9800")
            self.update_status(
                f"Spam clicking! Press {self.hotkey_manager.get_key_name(self.hotkey_manager.hotkey_spam)} to stop", 
                "red"
            )
    
    def stop_spam_click(self):
        """Stop spam clicking."""
        if self.spam_clicker.stop_spam_click():
            self.root.title(f"AutoClicker v{__version__}")
            self.banner_manager.hide_banner()
    
    def update_status(self, message, color="black"):
        """Update status label."""
        self.status_label.config(text=message, fg=color)
    
    def on_closing(self):
        """Cleanup when closing the application."""
        self.event_recorder.is_recording = False
        self.event_recorder.is_playing = False
        self.spam_clicker.is_spam_clicking = False
        
        self.banner_manager.cleanup()
        
        if self.event_recorder.mouse_listener:
            self.event_recorder.mouse_listener.stop()
        if self.event_recorder.keyboard_listener:
            self.event_recorder.keyboard_listener.stop()
        
        self.hotkey_manager.stop_listener()
        
        self.root.destroy()
