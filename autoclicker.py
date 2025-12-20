import tkinter as tk
from tkinter import ttk, scrolledtext
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading
import time
import json

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker with Recording")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Controllers
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Recording state
        self.is_recording = False
        self.is_playing = False
        self.recorded_events = []
        self.start_time = None
        
        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Playback settings
        self.loop_count = 1
        self.playback_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="AutoClicker with Recording", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Control Frame
        control_frame = tk.LabelFrame(self.root, text="Controls", padx=10, pady=10)
        control_frame.pack(padx=10, pady=5, fill="x")
        
        # Record Button
        self.record_btn = tk.Button(control_frame, text="Start Recording (F1)", 
                                    command=self.toggle_recording,
                                    bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                                    width=20, height=2)
        self.record_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Play/Stop Toggle Button
        self.play_btn = tk.Button(control_frame, text="Play Recording (F2)", 
                                  command=self.toggle_playback,
                                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                                  width=20, height=2)
        self.play_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Clear Button
        clear_btn = tk.Button(control_frame, text="Clear Recording", 
                             command=self.clear_recording,
                             bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                             width=20, height=2)
        clear_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Settings Frame
        settings_frame = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        settings_frame.pack(padx=10, pady=5, fill="x")
        
        # Loop Count
        tk.Label(settings_frame, text="Loop Count:").grid(row=0, column=0, sticky="w")
        self.loop_spinbox = tk.Spinbox(settings_frame, from_=0, to=100, width=10)
        self.loop_spinbox.grid(row=0, column=1, padx=5)
        self.loop_spinbox.delete(0, "end")
        self.loop_spinbox.insert(0, "1")
        
        tk.Label(settings_frame, text="(0 = Infinite)", fg="gray", font=("Arial", 8)).grid(row=0, column=2, sticky="w")
        
        # Status Frame
        status_frame = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                     font=("Arial", 10), fg="green")
        self.status_label.pack()
        
        # Event Log
        log_frame = tk.LabelFrame(self.root, text="Recorded Events", padx=10, pady=10)
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.event_log = scrolledtext.ScrolledText(log_frame, height=10, 
                                                    font=("Courier", 9))
        self.event_log.pack(fill="both", expand=True)
        
        # Info Label
        info_label = tk.Label(self.root, 
                             text="Hotkeys: F1=Toggle Record | F2=Toggle Play/Stop | ESC=Stop | Click/Type to record",
                             font=("Arial", 8), fg="gray")
        info_label.pack(pady=5)
        
        # Setup global hotkeys
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f1:
                    self.toggle_recording()
                elif key == keyboard.Key.f2:
                    self.toggle_playback()
                elif key == keyboard.Key.esc:
                    if self.is_playing:
                        self.stop_playback()
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
        
        self.record_btn.config(text="Stop Recording (F1)", bg="#f44336")
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
        
        self.record_btn.config(text="Start Recording (F1)", bg="#4CAF50")
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
        
        # Ignore hotkeys
        try:
            if key in [keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.esc]:
                return
        except:
            pass
        
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
        
        # Ignore hotkeys
        try:
            if key in [keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.esc]:
                return
        except:
            pass
        
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
        
        self.play_btn.config(text="Stop Playing (F2)", bg="#f44336")
        
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
                    
                    # Wait for the appropriate time
                    wait_time = event['timestamp'] - last_timestamp
                    if wait_time > 0:
                        time.sleep(wait_time)
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
            self.root.after(0, lambda: self.play_btn.config(text="Play Recording (F2)", bg="#2196F3"))
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
            self.play_btn.config(text="Play Recording (F2)", bg="#2196F3")
            self.update_status("Playback stopped!", "orange")
    
    def clear_recording(self):
        self.recorded_events = []
        self.event_log.delete(1.0, tk.END)
        self.update_status("Recording cleared!", "green")
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
    
    def on_closing(self):
        self.is_recording = False
        self.is_playing = False
        
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
