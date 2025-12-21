import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading
import time
import json
import os

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker with Recording")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        self.root.minsize(750, 450)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Controllers
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Recording state
        self.is_recording = False
        self.is_playing = False
        self.recorded_events = []
        self.start_time = None
        
        # Spam click state
        self.is_spam_clicking = False
        self.spam_click_thread = None
        
        # Banner window
        self.banner_window = None
        self.border_frames = []
        
        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Playback settings
        self.loop_count = 1
        self.playback_thread = None
        
        # Hotkey configuration
        self.hotkey_record = keyboard.Key.f1
        self.hotkey_play = keyboard.Key.f2
        self.hotkey_stop = keyboard.Key.esc
        self.hotkey_spam = keyboard.Key.f3
        self.capturing_hotkey = None
        
        self.setup_ui()
    
    def setup_ui(self):
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
        control_frame = tk.LabelFrame(left_panel, text="Controls", padx=8, pady=5)
        control_frame.pack(fill="x", pady=(0,5))
        
        # Record Button
        self.record_btn = tk.Button(control_frame, text=f"Record ({self.get_key_name(self.hotkey_record)})", 
                                    command=self.toggle_recording,
                                    bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
                                    height=1)
        self.record_btn.pack(fill="x", padx=3, pady=2)
        
        # Play/Stop Toggle Button
        self.play_btn = tk.Button(control_frame, text=f"Play ({self.get_key_name(self.hotkey_play)})", 
                                  command=self.toggle_playback,
                                  bg="#2196F3", fg="white", font=("Arial", 9, "bold"),
                                  height=1)
        self.play_btn.pack(fill="x", padx=3, pady=2)
        
        # Clear Button
        clear_btn = tk.Button(control_frame, text="Clear", 
                             command=self.clear_recording,
                             bg="#FF9800", fg="white", font=("Arial", 9, "bold"),
                             height=1)
        clear_btn.pack(fill="x", padx=3, pady=2)
        
        # Save/Load Frame
        saveload_frame = tk.Frame(control_frame)
        saveload_frame.pack(fill="x", padx=3, pady=2)
        
        # Save Button
        save_btn = tk.Button(saveload_frame, text="Save", 
                            command=self.save_recording,
                            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
                            height=1)
        save_btn.pack(side="left", fill="x", expand=True, padx=(0,2))
        
        # Load Button
        load_btn = tk.Button(saveload_frame, text="Load", 
                            command=self.load_recording,
                            bg="#009688", fg="white", font=("Arial", 9, "bold"),
                            height=1)
        load_btn.pack(side="left", fill="x", expand=True, padx=(2,0))
        
        # Settings Frame
        settings_frame = tk.LabelFrame(left_panel, text="Settings", padx=8, pady=5)
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
        
        # Hotkey Configuration Frame
        hotkey_frame = tk.LabelFrame(left_panel, text="Hotkeys", padx=8, pady=5)
        hotkey_frame.pack(fill="x")
        
        tk.Label(hotkey_frame, text="Record:", font=("Arial", 8)).grid(row=0, column=0, sticky="w", pady=2)
        self.record_hotkey_btn = tk.Button(hotkey_frame, text=self.get_key_name(self.hotkey_record),
                                           command=lambda: self.capture_hotkey('record'),
                                           width=10, font=("Arial", 8))
        self.record_hotkey_btn.grid(row=0, column=1, sticky="ew", pady=2, padx=(5,0))
        
        tk.Label(hotkey_frame, text="Play:", font=("Arial", 8)).grid(row=1, column=0, sticky="w", pady=2)
        self.play_hotkey_btn = tk.Button(hotkey_frame, text=self.get_key_name(self.hotkey_play),
                                         command=lambda: self.capture_hotkey('play'),
                                         width=10, font=("Arial", 8))
        self.play_hotkey_btn.grid(row=1, column=1, sticky="ew", pady=2, padx=(5,0))
        
        tk.Label(hotkey_frame, text="Stop:", font=("Arial", 8)).grid(row=2, column=0, sticky="w", pady=2)
        self.stop_hotkey_btn = tk.Button(hotkey_frame, text=self.get_key_name(self.hotkey_stop),
                                        command=lambda: self.capture_hotkey('stop'),
                                        width=10, font=("Arial", 8))
        self.stop_hotkey_btn.grid(row=2, column=1, sticky="ew", pady=2, padx=(5,0))
        
        tk.Label(hotkey_frame, text="Spam:", font=("Arial", 8)).grid(row=3, column=0, sticky="w", pady=2)
        self.spam_hotkey_btn = tk.Button(hotkey_frame, text=self.get_key_name(self.hotkey_spam),
                                        command=lambda: self.capture_hotkey('spam'),
                                        width=10, font=("Arial", 8))
        self.spam_hotkey_btn.grid(row=3, column=1, sticky="ew", pady=2, padx=(5,0))
        
        hotkey_frame.columnconfigure(1, weight=1)
        
        # Right Panel - Status and Event Log
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="left", fill="both", expand=True, padx=(2,5))
        
        # Status Frame
        status_frame = tk.LabelFrame(right_panel, text="Status", padx=8, pady=5)
        status_frame.pack(fill="x", pady=(0,5))
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                     font=("Arial", 9), fg="green")
        self.status_label.pack()
        
        # Event Log
        log_frame = tk.LabelFrame(right_panel, text="Recorded Events", padx=8, pady=5)
        log_frame.pack(fill="both", expand=True)
        
        self.event_log = scrolledtext.ScrolledText(log_frame, height=10, 
                                                    font=("Courier", 8), wrap=tk.WORD)
        self.event_log.pack(fill="both", expand=True)
        
        # Info Label at bottom
        self.info_label = tk.Label(self.root, 
                             text=self.get_hotkey_info(),
                             font=("Arial", 7), fg="gray")
        self.info_label.pack(pady=3)
        
        # Setup global hotkeys
        self.setup_hotkeys()
    
    def get_key_name(self, key):
        """Get a readable name for a key"""
        if hasattr(key, 'name'):
            return key.name.upper()
        return str(key).replace('Key.', '').upper()
    
    def parse_key_name(self, key_name):
        """Parse a key name string back to a keyboard Key object"""
        key_name_upper = key_name.upper()
        
        # Try to match keyboard.Key attributes
        for attr_name in dir(keyboard.Key):
            if not attr_name.startswith('_'):
                attr = getattr(keyboard.Key, attr_name)
                if hasattr(attr, 'name') and attr.name.upper() == key_name_upper:
                    return attr
        
        # If not found in keyboard.Key, try as KeyCode
        try:
            return keyboard.KeyCode.from_char(key_name.lower())
        except:
            # Default to F1 if parsing fails
            return keyboard.Key.f1
    
    def get_hotkey_info(self):
        """Get hotkey information string"""
        rec = self.get_key_name(self.hotkey_record)
        play = self.get_key_name(self.hotkey_play)
        stop = self.get_key_name(self.hotkey_stop)
        spam = self.get_key_name(self.hotkey_spam)
        return f"Hotkeys: {rec}=Toggle Record | {play}=Toggle Play/Stop | {stop}=Force Stop | {spam}=Toggle Spam Click"
    
    def capture_hotkey(self, hotkey_type):
        """Start capturing a new hotkey"""
        self.capturing_hotkey = hotkey_type
        
        if hotkey_type == 'record':
            self.record_hotkey_btn.config(text="Press key...", bg="yellow")
        elif hotkey_type == 'play':
            self.play_hotkey_btn.config(text="Press key...", bg="yellow")
        elif hotkey_type == 'stop':
            self.stop_hotkey_btn.config(text="Press key...", bg="yellow")
        elif hotkey_type == 'spam':
            self.spam_hotkey_btn.config(text="Press key...", bg="yellow")
        
        self.update_status("Press a key to set as hotkey...", "blue")
    
    def set_hotkey(self, key, hotkey_type):
        """Set a new hotkey"""
        if hotkey_type == 'record':
            self.hotkey_record = key
            self.record_hotkey_btn.config(text=self.get_key_name(key), bg="SystemButtonFace")
        elif hotkey_type == 'play':
            self.hotkey_play = key
            self.play_hotkey_btn.config(text=self.get_key_name(key), bg="SystemButtonFace")
        elif hotkey_type == 'stop':
            self.hotkey_stop = key
            self.stop_hotkey_btn.config(text=self.get_key_name(key), bg="SystemButtonFace")
        elif hotkey_type == 'spam':
            self.hotkey_spam = key
            self.spam_hotkey_btn.config(text=self.get_key_name(key), bg="SystemButtonFace")
        
        self.capturing_hotkey = None
        self.info_label.config(text=self.get_hotkey_info())
        self.update_status(f"Hotkey updated to {self.get_key_name(key)}", "green")
        
        # Restart hotkey listener with new keys
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        # Stop existing listener if any
        if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
            self.hotkey_listener.stop()
        
        def on_press(key):
            try:
                # If capturing a hotkey, set it
                if self.capturing_hotkey:
                    self.root.after(0, lambda: self.set_hotkey(key, self.capturing_hotkey))
                    return
                
                # Normal hotkey handling
                if key == self.hotkey_record:
                    self.toggle_recording()
                elif key == self.hotkey_play:
                    self.toggle_playback()
                elif key == self.hotkey_stop:
                    if self.is_playing:
                        self.stop_playback()
                elif key == self.hotkey_spam:
                    self.toggle_spam_click()
            except:
                pass
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
    
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        if self.is_playing:
            self.update_status("Cannot record while playing!", "red")
            return
        
        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        
        # Update UI indicators
        self.root.title("🔴 RECORDING - AutoClicker")
        self.show_banner("● RECORDING", "#f44336")
        
        self.record_btn.config(text=f"Stop ({self.get_key_name(self.hotkey_record)})", bg="#f44336")
        self.update_status("Recording... Click and type!", "red")
        self.event_log.delete(1.0, tk.END)
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move
        )
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
    
    def stop_recording(self):
        self.is_recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Update UI indicators
        self.root.title("AutoClicker with Recording")
        self.hide_banner()
        
        self.record_btn.config(text=f"Record ({self.get_key_name(self.hotkey_record)})", bg="#4CAF50")
        self.update_status(f"Recording stopped. {len(self.recorded_events)} events recorded.", "green")
    
    def on_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        
        timestamp = time.time() - self.start_time
        event = {
            'type': 'mouse_click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'timestamp': timestamp
        }
        self.recorded_events.append(event)
        
        action = "Press" if pressed else "Release"
        log_text = f"[{timestamp:.2f}s] Mouse {action}: {button} at ({x}, {y})\n"
        self.event_log.insert(tk.END, log_text)
        self.event_log.see(tk.END)
    
    def on_move(self, x, y):
        # We don't record all movements to avoid too many events
        # You can enable this if needed
        pass
    
    def on_key_press(self, key):
        if not self.is_recording:
            return
        
        # Ignore configured hotkeys
        if key in [self.hotkey_record, self.hotkey_play, self.hotkey_stop]:
            return
        
        timestamp = time.time() - self.start_time
        
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)
        
        event = {
            'type': 'key_press',
            'key': key_name,
            'timestamp': timestamp
        }
        self.recorded_events.append(event)
        
        log_text = f"[{timestamp:.2f}s] Key Press: {key_name}\n"
        self.event_log.insert(tk.END, log_text)
        self.event_log.see(tk.END)
    
    def on_key_release(self, key):
        if not self.is_recording:
            return
        
        # Ignore configured hotkeys
        if key in [self.hotkey_record, self.hotkey_play, self.hotkey_stop]:
            return
        
        timestamp = time.time() - self.start_time
        
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)
        
        event = {
            'type': 'key_release',
            'key': key_name,
            'timestamp': timestamp
        }
        self.recorded_events.append(event)
        
        log_text = f"[{timestamp:.2f}s] Key Release: {key_name}\n"
        self.event_log.insert(tk.END, log_text)
        self.event_log.see(tk.END)
    
    def toggle_playback(self):
        if self.is_playing:
            self.stop_playback()
        else:
            self.play_recording()
    
    def play_recording(self):
        if self.is_recording:
            self.update_status("Stop recording first!", "red")
            return
        
        if not self.recorded_events:
            self.update_status("No events to play!", "red")
            return
        
        if self.is_playing:
            return
        
        self.loop_count = int(self.loop_spinbox.get())
        self.is_playing = True
        
        # Update UI indicators
        self.root.title("▶️ PLAYING - AutoClicker")
        self.show_banner("▶ PLAYING", "#2196F3")
        
        self.play_btn.config(text=f"Stop ({self.get_key_name(self.hotkey_play)})", bg="#f44336")
        
        if self.loop_count == 0:
            self.update_status("Playing recording (Infinite loops)...", "blue")
        else:
            self.update_status(f"Playing recording ({self.loop_count} loops)...", "blue")
        
        self.playback_thread = threading.Thread(target=self.playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def playback_worker(self):
        try:
            loop = 0
            while True:
                if not self.is_playing:
                    break
                
                # Check if we've reached the loop limit (if not infinite)
                if self.loop_count > 0 and loop >= self.loop_count:
                    break
                
                # Add delay between loops (not before the first loop)
                if loop > 0:
                    delay = float(self.delay_spinbox.get())
                    if delay > 0:
                        time.sleep(delay)
                
                loop += 1
                
                if self.loop_count == 0:
                    self.root.after(0, self.update_status, 
                                   f"Playing loop {loop} (Infinite)...", "blue")
                else:
                    self.root.after(0, self.update_status, 
                                   f"Playing loop {loop}/{self.loop_count}...", "blue")
                
                last_timestamp = 0
                for event in self.recorded_events:
                    if not self.is_playing:
                        break
                    
                    # Wait for the appropriate time with speed multiplier
                    wait_time = event['timestamp'] - last_timestamp
                    if wait_time > 0:
                        # Apply speed multiplier (higher = faster, lower = slower)
                        speed = float(self.speed_spinbox.get())
                        adjusted_wait = wait_time / speed if speed > 0 else wait_time
                        time.sleep(adjusted_wait)
                    last_timestamp = event['timestamp']
                    
                    # Execute the event
                    if event['type'] == 'mouse_click':
                        self.replay_mouse_click(event)
                    elif event['type'] == 'key_press':
                        self.replay_key_press(event)
                    elif event['type'] == 'key_release':
                        self.replay_key_release(event)
        
        except Exception as e:
            self.root.after(0, self.update_status, f"Error: {str(e)}", "red")
        
        finally:
            self.is_playing = False
            self.root.after(0, lambda: self.root.title("AutoClicker with Recording"))
            self.root.after(0, self.hide_banner)
            self.root.after(0, lambda: self.play_btn.config(text=f"Play ({self.get_key_name(self.hotkey_play)})", bg="#2196F3"))
            self.root.after(0, self.update_status, "Playback completed!", "green")
    
    def replay_mouse_click(self, event):
        x, y = event['x'], event['y']
        button_str = event['button']
        pressed = event['pressed']
        
        # Move mouse to position
        self.mouse_controller.position = (x, y)
        
        # Parse button
        if 'left' in button_str.lower():
            button = Button.left
        elif 'right' in button_str.lower():
            button = Button.right
        elif 'middle' in button_str.lower():
            button = Button.middle
        else:
            button = Button.left
        
        # Click
        if pressed:
            self.mouse_controller.press(button)
        else:
            self.mouse_controller.release(button)
    
    def replay_key_press(self, event):
        key_name = event['key']
        
        try:
            # Try to parse as special key
            if key_name.startswith("Key."):
                key_attr = key_name.split('.')[1]
                key = getattr(Key, key_attr, None)
                if key:
                    self.keyboard_controller.press(key)
                    return
            
            # Regular character
            self.keyboard_controller.press(key_name)
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
    
    def replay_key_release(self, event):
        key_name = event['key']
        
        try:
            # Try to parse as special key
            if key_name.startswith("Key."):
                key_attr = key_name.split('.')[1]
                key = getattr(Key, key_attr, None)
                if key:
                    self.keyboard_controller.release(key)
                    return
            
            # Regular character
            self.keyboard_controller.release(key_name)
        except Exception as e:
            print(f"Error releasing key {key_name}: {e}")
    
    def stop_playback(self):
        if self.is_playing:
            self.is_playing = False
            self.root.title("AutoClicker with Recording")
            self.hide_banner()
            self.play_btn.config(text=f"Play ({self.get_key_name(self.hotkey_play)})", bg="#2196F3")
            self.update_status("Playback stopped!", "orange")
    
    def clear_recording(self):
        self.recorded_events = []
        self.event_log.delete(1.0, tk.END)
        self.update_status("Recording cleared!", "green")
    
    def save_recording(self):
        """Save recorded events and configuration to a JSON file"""
        if not self.recorded_events:
            messagebox.showwarning("No Recording", "There are no recorded events to save!")
            return
        
        if self.is_recording:
            messagebox.showwarning("Recording Active", "Please stop recording before saving!")
            return
        
        if self.is_playing:
            messagebox.showwarning("Playback Active", "Please stop playback before saving!")
            return
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".aclk",
            filetypes=[("AutoClicker Recording", "*.aclk"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Recording As"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Prepare configuration data
            config_data = {
                "events": self.recorded_events,
                "config": {
                    "loops": int(self.loop_spinbox.get()),
                    "delay": float(self.delay_spinbox.get()),
                    "speed": float(self.speed_spinbox.get()),
                    "hotkeys": {
                        "record": self.get_key_name(self.hotkey_record),
                        "play": self.get_key_name(self.hotkey_play),
                        "stop": self.get_key_name(self.hotkey_stop),
                        "spam": self.get_key_name(self.hotkey_spam)
                    }
                }
            }
            
            # Save events and config to JSON file
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            messagebox.showinfo("Success", f"Recording and config saved successfully!\n{len(self.recorded_events)} events saved to:\n{os.path.basename(file_path)}")
            self.update_status(f"Recording and config saved: {os.path.basename(file_path)}", "green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recording:\n{str(e)}")
            self.update_status(f"Error saving recording: {str(e)}", "red")
    
    def load_recording(self):
        """Load recorded events and configuration from a JSON file"""
        if self.is_recording:
            messagebox.showwarning("Recording Active", "Please stop recording before loading!")
            return
        
        if self.is_playing:
            messagebox.showwarning("Playback Active", "Please stop playback before loading!")
            return
        
        # Ask user for file to load
        file_path = filedialog.askopenfilename(
            filetypes=[("AutoClicker Recording", "*.aclk"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Recording"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Load data from JSON file
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
            
            # Check if it's the new format (with config) or old format (just events)
            if isinstance(loaded_data, dict) and 'events' in loaded_data:
                # New format: has events and config
                loaded_events = loaded_data['events']
                config = loaded_data.get('config', {})
                
                # Load timing configuration if available
                if 'loops' in config:
                    self.loop_spinbox.delete(0, "end")
                    self.loop_spinbox.insert(0, str(config['loops']))
                if 'delay' in config:
                    self.delay_spinbox.delete(0, "end")
                    self.delay_spinbox.insert(0, str(config['delay']))
                if 'speed' in config:
                    self.speed_spinbox.delete(0, "end")
                    self.speed_spinbox.insert(0, str(config['speed']))
                
                # Load hotkey configuration if available
                if 'hotkeys' in config:
                    hotkeys = config['hotkeys']
                    if 'record' in hotkeys:
                        self.hotkey_record = self.parse_key_name(hotkeys['record'])
                        self.record_hotkey_btn.config(text=hotkeys['record'])
                        self.record_btn.config(text=f"Record ({hotkeys['record']})")
                    if 'play' in hotkeys:
                        self.hotkey_play = self.parse_key_name(hotkeys['play'])
                        self.play_hotkey_btn.config(text=hotkeys['play'])
                        self.play_btn.config(text=f"Play ({hotkeys['play']})")
                    if 'stop' in hotkeys:
                        self.hotkey_stop = self.parse_key_name(hotkeys['stop'])
                        self.stop_hotkey_btn.config(text=hotkeys['stop'])
                    if 'spam' in hotkeys:
                        self.hotkey_spam = self.parse_key_name(hotkeys['spam'])
                        self.spam_hotkey_btn.config(text=hotkeys['spam'])
                    
                    # Update hotkey info and restart listeners
                    self.info_label.config(text=self.get_hotkey_info())
                    self.setup_hotkeys()
            else:
                # Old format: just events
                loaded_events = loaded_data
            
            # Validate the loaded events
            if not isinstance(loaded_events, list):
                raise ValueError("Invalid file format: expected a list of events")
            
            # Basic validation of event structure
            for event in loaded_events:
                if not isinstance(event, dict):
                    raise ValueError("Invalid event format: expected dictionary")
                if 'type' not in event or 'timestamp' not in event:
                    raise ValueError("Invalid event format: missing required fields")
            
            # Clear current recording and load new one
            self.recorded_events = loaded_events
            self.event_log.delete(1.0, tk.END)
            
            # Display loaded events in the log
            for event in self.recorded_events:
                timestamp = event['timestamp']
                if event['type'] == 'mouse_click':
                    action = "Press" if event['pressed'] else "Release"
                    log_text = f"[{timestamp:.2f}s] Mouse {action}: {event['button']} at ({event['x']}, {event['y']})\n"
                elif event['type'] == 'key_press':
                    log_text = f"[{timestamp:.2f}s] Key Press: {event['key']}\n"
                elif event['type'] == 'key_release':
                    log_text = f"[{timestamp:.2f}s] Key Release: {event['key']}\n"
                else:
                    log_text = f"[{timestamp:.2f}s] Unknown event type: {event['type']}\n"
                
                self.event_log.insert(tk.END, log_text)
            
            self.event_log.see(tk.END)
            
            messagebox.showinfo("Success", f"Recording and config loaded successfully!\n{len(self.recorded_events)} events loaded from:\n{os.path.basename(file_path)}")
            self.update_status(f"Recording and config loaded: {os.path.basename(file_path)} ({len(self.recorded_events)} events)", "green")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to parse JSON file:\n{str(e)}")
            self.update_status(f"Error loading recording: Invalid JSON", "red")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recording:\n{str(e)}")
            self.update_status(f"Error loading recording: {str(e)}", "red")
    
    def toggle_spam_click(self):
        """Toggle rapid-fire left click spam"""
        if self.is_spam_clicking:
            self.stop_spam_click()
        else:
            self.start_spam_click()
    
    def start_spam_click(self):
        """Start rapid-fire left clicking"""
        if self.is_recording:
            self.update_status("Cannot spam click while recording!", "red")
            return
        
        self.is_spam_clicking = True
        
        # Update UI indicators
        self.root.title("⚡ SPAM CLICKING - AutoClicker")
        self.show_banner("⚡ SPAM CLICKING", "#FF9800")
        
        self.update_status(f"Spam clicking! Press {self.get_key_name(self.hotkey_spam)} to stop", "red")
        
        self.spam_click_thread = threading.Thread(target=self.spam_click_worker)
        self.spam_click_thread.daemon = True
        self.spam_click_thread.start()
    
    def spam_click_worker(self):
        """Worker thread for rapid-fire clicking"""
        try:
            while self.is_spam_clicking:
                self.mouse_controller.click(Button.left, 1)
                time.sleep(0.01)  # 10ms delay = 100 clicks per second
        except Exception as e:
            self.root.after(0, self.update_status, f"Error: {str(e)}", "red")
    
    def stop_spam_click(self):
        """Stop spam clicking"""
        if self.is_spam_clicking:
            self.is_spam_clicking = False
            self.root.title("AutoClicker with Recording")
            self.hide_banner()
            self.update_status("Spam clicking stopped!", "green")
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
    
    def show_banner(self, text, bg_color):
        """Show compact always-on-top banner at top-left with screen border"""
        if self.banner_window:
            self.hide_banner()
        
        # Create compact banner at top-left
        self.banner_window = tk.Toplevel(self.root)
        self.banner_window.overrideredirect(True)  # Remove window decorations
        self.banner_window.attributes('-topmost', True)  # Always on top
        
        # Create compact banner label
        banner_label = tk.Label(self.banner_window, text=text,
                               font=("Arial", 11, "bold"),
                               bg=bg_color, fg="white",
                               padx=15, pady=8)
        banner_label.pack()
        
        # Update geometry after packing to get actual size
        self.banner_window.update_idletasks()
        
        # Position at top-left corner
        self.banner_window.geometry(f"+10+10")
        
        # Create thin border frames around screen edges
        screen_width = self.banner_window.winfo_screenwidth()
        screen_height = self.banner_window.winfo_screenheight()
        border_thickness = 4
        
        # Top border
        top_frame = tk.Toplevel(self.root)
        top_frame.overrideredirect(True)
        top_frame.attributes('-topmost', True)
        top_frame.configure(bg=bg_color)
        top_frame.geometry(f"{screen_width}x{border_thickness}+0+0")
        self.border_frames.append(top_frame)
        
        # Bottom border
        bottom_frame = tk.Toplevel(self.root)
        bottom_frame.overrideredirect(True)
        bottom_frame.attributes('-topmost', True)
        bottom_frame.configure(bg=bg_color)
        bottom_frame.geometry(f"{screen_width}x{border_thickness}+0+{screen_height-border_thickness}")
        self.border_frames.append(bottom_frame)
        
        # Left border
        left_frame = tk.Toplevel(self.root)
        left_frame.overrideredirect(True)
        left_frame.attributes('-topmost', True)
        left_frame.configure(bg=bg_color)
        left_frame.geometry(f"{border_thickness}x{screen_height}+0+0")
        self.border_frames.append(left_frame)
        
        # Right border
        right_frame = tk.Toplevel(self.root)
        right_frame.overrideredirect(True)
        right_frame.attributes('-topmost', True)
        right_frame.configure(bg=bg_color)
        right_frame.geometry(f"{border_thickness}x{screen_height}+{screen_width-border_thickness}+0")
        self.border_frames.append(right_frame)
    
    def hide_banner(self):
        """Hide and destroy the banner window and border frames"""
        if self.banner_window:
            self.banner_window.destroy()
            self.banner_window = None
        
        for frame in self.border_frames:
            frame.destroy()
        self.border_frames = []
    
    def on_closing(self):
        self.is_recording = False
        self.is_playing = False
        self.is_spam_clicking = False
        
        self.hide_banner()
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
