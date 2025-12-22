"""Event recording and playback functionality."""

from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading
import time


class EventRecorder:
    """Manages recording and playback of mouse and keyboard events."""
    
    def __init__(self):
        # Controllers
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Recording state
        self.is_recording = False
        self.is_playing = False
        self.recorded_events = []
        self.start_time = None
        
        # Track pressed buttons/keys during playback for cleanup
        self._pressed_mouse_buttons = set()
        self._pressed_keys = set()
        
        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Playback settings
        self.loop_count = 1
        self.loop_delay = 0.0
        self.playback_speed = 1.0
        self.playback_thread = None
        
        # Hotkeys to ignore during recording
        self.ignored_keys = []
        
        # Callbacks
        self.on_event_callback = None
        self.on_status_callback = None
        self.on_playback_complete_callback = None
    
    def set_callbacks(self, on_event=None, on_status=None, on_playback_complete=None):
        """Set callback functions for events."""
        if on_event:
            self.on_event_callback = on_event
        if on_status:
            self.on_status_callback = on_status
        if on_playback_complete:
            self.on_playback_complete_callback = on_playback_complete
    
    def set_ignored_keys(self, keys):
        """Set keys to ignore during recording."""
        self.ignored_keys = keys
    
    def start_recording(self):
        """Start recording mouse and keyboard events."""
        if self.is_playing:
            if self.on_status_callback:
                self.on_status_callback("Cannot record while playing!", "red")
            return False
        
        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move
        )
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        if self.on_status_callback:
            self.on_status_callback("Recording... Click and type!", "red")
        
        return True
    
    def stop_recording(self):
        """Stop recording events."""
        self.is_recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        if self.on_status_callback:
            self.on_status_callback(f"Recording stopped. {len(self.recorded_events)} events recorded.", "green")
        
        return len(self.recorded_events)
    
    def _on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
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
        
        if self.on_event_callback:
            action = "Press" if pressed else "Release"
            log_text = f"[{timestamp:.2f}s] Mouse {action}: {button} at ({x}, {y})\n"
            self.on_event_callback(log_text)
    
    def _on_move(self, x, y):
        """Handle mouse move events (currently not recorded)."""
        pass
    
    def _on_key_press(self, key):
        """Handle keyboard key press events."""
        if not self.is_recording:
            return
        
        # Ignore configured hotkeys
        if key in self.ignored_keys:
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
        
        if self.on_event_callback:
            log_text = f"[{timestamp:.2f}s] Key Press: {key_name}\n"
            self.on_event_callback(log_text)
    
    def _on_key_release(self, key):
        """Handle keyboard key release events."""
        if not self.is_recording:
            return
        
        # Ignore configured hotkeys
        if key in self.ignored_keys:
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
        
        if self.on_event_callback:
            log_text = f"[{timestamp:.2f}s] Key Release: {key_name}\n"
            self.on_event_callback(log_text)
    
    def start_playback(self, loop_count=1, loop_delay=0.0, playback_speed=1.0):
        """Start playing back recorded events."""
        if self.is_recording:
            if self.on_status_callback:
                self.on_status_callback("Stop recording first!", "red")
            return False
        
        if not self.recorded_events:
            if self.on_status_callback:
                self.on_status_callback("No events to play!", "red")
            return False
        
        if self.is_playing:
            return False
        
        self.loop_count = loop_count
        self.loop_delay = loop_delay
        self.playback_speed = playback_speed
        self.is_playing = True
        
        if self.on_status_callback:
            if self.loop_count == 0:
                self.on_status_callback("Playing recording (Infinite loops)...", "blue")
            else:
                self.on_status_callback(f"Playing recording ({self.loop_count} loops)...", "blue")
        
        self.playback_thread = threading.Thread(target=self._playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
        
        return True
    
    def _playback_worker(self):
        """Worker thread for playing back events."""
        # Clear any stale pressed state at start
        self._pressed_mouse_buttons.clear()
        self._pressed_keys.clear()
        
        try:
            loop = 0
            while True:
                if not self.is_playing:
                    break
                
                # Check if we've reached the loop limit (if not infinite)
                if self.loop_count > 0 and loop >= self.loop_count:
                    break
                
                # Add delay between loops (not before the first loop)
                if loop > 0 and self.loop_delay > 0:
                    time.sleep(self.loop_delay)
                
                loop += 1
                
                if self.on_status_callback:
                    if self.loop_count == 0:
                        self.on_status_callback(f"Playing loop {loop} (Infinite)...", "blue")
                    else:
                        self.on_status_callback(f"Playing loop {loop}/{self.loop_count}...", "blue")
                
                last_timestamp = 0
                for event in self.recorded_events:
                    if not self.is_playing:
                        break
                    
                    # Wait for the appropriate time with speed multiplier
                    wait_time = event['timestamp'] - last_timestamp
                    if wait_time > 0:
                        adjusted_wait = wait_time / self.playback_speed if self.playback_speed > 0 else wait_time
                        time.sleep(adjusted_wait)
                    last_timestamp = event['timestamp']
                    
                    # Execute the event
                    if event['type'] == 'mouse_click':
                        self._replay_mouse_click(event)
                    elif event['type'] == 'key_press':
                        self._replay_key_press(event)
                    elif event['type'] == 'key_release':
                        self._replay_key_release(event)
        
        except Exception as e:
            if self.on_status_callback:
                self.on_status_callback(f"Error: {str(e)}", "red")
        
        finally:
            # Always release any held buttons/keys when playback ends
            self._release_all_pressed()
            self.is_playing = False
            if self.on_playback_complete_callback:
                self.on_playback_complete_callback()
            if self.on_status_callback:
                self.on_status_callback("Playback completed!", "green")
    
    def _replay_mouse_click(self, event):
        """Replay a mouse click event."""
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
        
        # Click and track state
        if pressed:
            self.mouse_controller.press(button)
            self._pressed_mouse_buttons.add(button)
        else:
            self.mouse_controller.release(button)
            self._pressed_mouse_buttons.discard(button)
    
    def _replay_key_press(self, event):
        """Replay a keyboard key press event."""
        key_name = event['key']
        
        try:
            # Try to parse as special key
            if key_name.startswith("Key."):
                key_attr = key_name.split('.')[1]
                key = getattr(Key, key_attr, None)
                if key:
                    self.keyboard_controller.press(key)
                    self._pressed_keys.add(key)
                    return
            
            # Regular character
            self.keyboard_controller.press(key_name)
            self._pressed_keys.add(key_name)
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
    
    def _replay_key_release(self, event):
        """Replay a keyboard key release event."""
        key_name = event['key']
        
        try:
            # Try to parse as special key
            if key_name.startswith("Key."):
                key_attr = key_name.split('.')[1]
                key = getattr(Key, key_attr, None)
                if key:
                    self.keyboard_controller.release(key)
                    self._pressed_keys.discard(key)
                    return
            
            # Regular character
            self.keyboard_controller.release(key_name)
            self._pressed_keys.discard(key_name)
        except Exception as e:
            print(f"Error releasing key {key_name}: {e}")
    
    def stop_playback(self):
        """Stop playing back events and release any held buttons/keys."""
        if self.is_playing:
            self.is_playing = False
            
            # Release any mouse buttons that are still pressed
            self._release_all_pressed()
            
            if self.on_status_callback:
                self.on_status_callback("Playback stopped!", "orange")
            return True
        return False
    
    def _release_all_pressed(self):
        """Release all pressed mouse buttons and keyboard keys."""
        # Release mouse buttons
        for button in list(self._pressed_mouse_buttons):
            try:
                self.mouse_controller.release(button)
            except Exception:
                pass
        self._pressed_mouse_buttons.clear()
        
        # Release keyboard keys
        for key in list(self._pressed_keys):
            try:
                self.keyboard_controller.release(key)
            except Exception:
                pass
        self._pressed_keys.clear()
    
    def clear_recording(self):
        """Clear all recorded events."""
        self.recorded_events = []
        if self.on_status_callback:
            self.on_status_callback("Recording cleared!", "green")
    
    def get_events(self):
        """Get the list of recorded events."""
        return self.recorded_events
    
    def set_events(self, events):
        """Set the list of recorded events."""
        self.recorded_events = events
