"""Event recording and playback functionality."""

from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading
import time

from utils.key_utils import get_key_info, KeyInfo

# Set to True to enable debug logging
DEBUG = False


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
        self.on_live_input_callback = None  # For showing live key/mouse input
        self.on_delay_countdown_callback = None  # For showing countdown during loop delay
    
    def set_callbacks(self, on_event=None, on_status=None, on_playback_complete=None, on_live_input=None, on_delay_countdown=None):
        """Set callback functions for events."""
        if on_event:
            self.on_event_callback = on_event
        if on_status:
            self.on_status_callback = on_status
        if on_playback_complete:
            self.on_playback_complete_callback = on_playback_complete
        if on_live_input:
            self.on_live_input_callback = on_live_input
        if on_delay_countdown:
            self.on_delay_countdown_callback = on_delay_countdown
    
    def set_ignored_keys(self, keys):
        """Set keys to ignore during recording.
        
        Args:
            keys: List of KeyInfo objects or similar objects with normalized_key attribute
        """
        self.ignored_keys = keys
    
    def _is_ignored_key(self, key):
        """Check if a key should be ignored during recording."""
        key_info = get_key_info(key)
        for ignored in self.ignored_keys:
            if hasattr(ignored, 'normalized_key'):
                if key_info.normalized_key == ignored.normalized_key:
                    return True
            elif ignored == key:
                # Fallback for direct comparison
                return True
        return False
    
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
        
        action = "Press" if pressed else "Release"
        button_name = str(button).replace("Button.", "").upper()
        
        if self.on_event_callback:
            log_text = f"[{timestamp:.2f}s] Mouse {action}: {button} at ({x}, {y})\n"
            self.on_event_callback(log_text)
        
        # Live input callback for banner display
        if self.on_live_input_callback and pressed:
            self.on_live_input_callback("mouse", f"🖱 {button_name} ({x}, {y})")
    
    def _on_move(self, x, y):
        """Handle mouse move events (currently not recorded)."""
        pass
    
    def _get_key_names(self, key):
        """Get key name and display name, differentiating numpad keys.
        
        Returns:
            tuple: (key_name for recording, display_name for UI)
        """
        key_str = str(key)
        
        # X11 numpad keycodes (when NumLock is OFF or for special numpad keys)
        # These are X11 keysyms for numpad keys
        x11_numpad_map = {
            65437: ('num_5', 'NUM 5'),      # KP_5 / KP_Begin
            65436: ('num_4', 'NUM 4'),      # KP_4 / KP_Left
            65438: ('num_6', 'NUM 6'),      # KP_6 / KP_Right
            65432: ('num_8', 'NUM 8'),      # KP_8 / KP_Up
            65433: ('num_2', 'NUM 2'),      # KP_2 / KP_Down
            65434: ('num_9', 'NUM 9'),      # KP_9 / KP_Prior
            65435: ('num_3', 'NUM 3'),      # KP_3 / KP_Next
            65429: ('num_7', 'NUM 7'),      # KP_7 / KP_Home
            65430: ('num_1', 'NUM 1'),      # KP_1 / KP_End
            65438: ('num_0', 'NUM 0'),      # KP_0 / KP_Insert
            65439: ('num_decimal', 'NUM .'), # KP_Decimal / KP_Delete
            65451: ('num_add', 'NUM +'),     # KP_Add
            65453: ('num_subtract', 'NUM -'), # KP_Subtract
            65450: ('num_multiply', 'NUM *'), # KP_Multiply
            65455: ('num_divide', 'NUM /'),   # KP_Divide
            65421: ('num_enter', 'NUM ENTER'), # KP_Enter
        }
        
        # Check if it's an X11 numpad keycode (appears as <number>)
        if key_str.startswith('<') and key_str.endswith('>'):
            try:
                keycode = int(key_str[1:-1])
                if keycode in x11_numpad_map:
                    return x11_numpad_map[keycode]
                # Unknown numpad/special key
                return (key_str, f'KEY {keycode}')
            except ValueError:
                pass
        
        # Check for Key.* numpad constants
        if 'num_lock' in key_str.lower():
            return ('Key.num_lock', 'NUM LOCK')
        
        # Try to get character
        try:
            char = key.char
            if char is not None:
                vk = getattr(key, 'vk', None)
                
                # On Linux/X11: vk=None typically means numpad, vk=number means regular
                # Check if it's a digit or numpad symbol
                if char in '0123456789':
                    if vk is None:
                        return (f'num_{char}', f'NUM {char}')
                    else:
                        return (char, char)
                elif char in '.,':
                    # Period or comma - could be numpad decimal (varies by locale)
                    # In some locales numpad decimal outputs comma instead of period
                    if vk is None:
                        return ('num_decimal', f'NUM {char}')
                    else:
                        return (char, char)
                elif char == '+':
                    if vk is None:
                        return ('num_add', 'NUM +')
                    else:
                        return (char, '+')
                elif char == '-':
                    if vk is None:
                        return ('num_subtract', 'NUM -')
                    else:
                        return (char, '-')
                elif char == '*':
                    if vk is None:
                        return ('num_multiply', 'NUM *')
                    else:
                        return (char, '*')
                elif char == '/':
                    if vk is None:
                        return ('num_divide', 'NUM /')
                    else:
                        return (char, '/')
                else:
                    return (char, char)
        except AttributeError:
            pass
        
        # Handle special keys
        key_name = str(key)
        display_name = key_name.replace("Key.", "").upper()
        
        # Make display names more readable
        display_replacements = {
            'SPACE': 'SPACE',
            'ENTER': 'ENTER',
            'BACKSPACE': 'BACKSPACE',
            'TAB': 'TAB',
            'CAPS_LOCK': 'CAPS',
            'SHIFT': 'SHIFT',
            'SHIFT_L': 'L-SHIFT',
            'SHIFT_R': 'R-SHIFT',
            'CTRL': 'CTRL',
            'CTRL_L': 'L-CTRL',
            'CTRL_R': 'R-CTRL',
            'ALT': 'ALT',
            'ALT_L': 'L-ALT',
            'ALT_R': 'R-ALT',
            'ALT_GR': 'ALT GR',
            'CMD': 'CMD',
            'CMD_L': 'L-CMD',
            'CMD_R': 'R-CMD',
            'DELETE': 'DEL',
            'INSERT': 'INS',
            'HOME': 'HOME',
            'END': 'END',
            'PAGE_UP': 'PG UP',
            'PAGE_DOWN': 'PG DN',
            'UP': '↑',
            'DOWN': '↓',
            'LEFT': '←',
            'RIGHT': '→',
            'ESC': 'ESC',
            'ESCAPE': 'ESC',
            'PRINT_SCREEN': 'PRTSC',
            'SCROLL_LOCK': 'SCRLK',
            'PAUSE': 'PAUSE',
        }
        
        if display_name in display_replacements:
            display_name = display_replacements[display_name]
        
        if display_name in display_replacements:
            display_name = display_replacements[display_name]
        
        return (key_name, display_name)
    
    def _on_key_press(self, key):
        """Handle keyboard key press events."""
        if not self.is_recording:
            return
        
        # Ignore configured hotkeys
        if self._is_ignored_key(key):
            return
        
        timestamp = time.time() - self.start_time
        
        key_name, display_name = self._get_key_names(key)
        
        event = {
            'type': 'key_press',
            'key': key_name,
            'timestamp': timestamp
        }
        self.recorded_events.append(event)
        
        if self.on_event_callback:
            log_text = f"[{timestamp:.2f}s] Key Press: {key_name}\n"
            self.on_event_callback(log_text)
        
        # Live input callback for banner display
        if self.on_live_input_callback:
            self.on_live_input_callback("key", f"⌨ {display_name}")
    
    def _on_key_release(self, key):
        """Handle keyboard key release events."""
        if not self.is_recording:
            return
        
        # Ignore configured hotkeys
        if self._is_ignored_key(key):
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
        
        # DEBUG: Log playback settings
        if DEBUG:
            print(f"[DEBUG] _playback_worker started")
            print(f"[DEBUG] self.loop_count = {self.loop_count} (type: {type(self.loop_count)})")
            print(f"[DEBUG] self.loop_delay = {self.loop_delay}")
            print(f"[DEBUG] self.playback_speed = {self.playback_speed}")
            print(f"[DEBUG] Number of events: {len(self.recorded_events)}")
        
        try:
            loop = 0
            while True:
                if DEBUG:
                    print(f"[DEBUG] Loop iteration: loop={loop}, loop_count={self.loop_count}")
                if not self.is_playing:
                    if DEBUG:
                        print(f"[DEBUG] Breaking: is_playing is False")
                    break
                
                # Check if we've reached the loop limit (if not infinite)
                if self.loop_count > 0 and loop >= self.loop_count:
                    if DEBUG:
                        print(f"[DEBUG] Breaking: loop ({loop}) >= loop_count ({self.loop_count})")
                    break
                
                # Add delay between loops (not before the first loop)
                if loop > 0 and self.loop_delay > 0:
                    if DEBUG:
                        print(f"[DEBUG] Sleeping for loop_delay: {self.loop_delay}")
                    # Countdown timer with banner updates
                    remaining = self.loop_delay
                    while remaining > 0 and self.is_playing:
                        if self.on_delay_countdown_callback:
                            self.on_delay_countdown_callback(remaining)
                        # Sleep in small increments for responsive countdown
                        sleep_time = min(0.1, remaining)
                        time.sleep(sleep_time)
                        remaining -= sleep_time
                    # Clear countdown when done
                    if self.on_delay_countdown_callback and self.is_playing:
                        self.on_delay_countdown_callback(0)
                
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
            button_name = "LEFT"
        elif 'right' in button_str.lower():
            button = Button.right
            button_name = "RIGHT"
        elif 'middle' in button_str.lower():
            button = Button.middle
            button_name = "MIDDLE"
        else:
            button = Button.left
            button_name = "LEFT"
        
        # Live input callback for banner display (only on press)
        if self.on_live_input_callback and pressed:
            self.on_live_input_callback("mouse", f"🖱 {button_name} ({x}, {y})")
        
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
        display_name = self._get_display_name_for_replay(key_name)
        
        try:
            # Handle numpad keys
            if key_name.startswith('num_'):
                # Map numpad key names back to actual keys
                numpad_chars = {
                    'num_0': '0', 'num_1': '1', 'num_2': '2', 'num_3': '3',
                    'num_4': '4', 'num_5': '5', 'num_6': '6', 'num_7': '7',
                    'num_8': '8', 'num_9': '9', 'num_decimal': '.',
                    'num_add': '+', 'num_subtract': '-',
                    'num_multiply': '*', 'num_divide': '/',
                }
                if key_name in numpad_chars:
                    char = numpad_chars[key_name]
                    self.keyboard_controller.press(char)
                    self._pressed_keys.add(char)
                    if self.on_live_input_callback:
                        self.on_live_input_callback("key", f"⌨ {display_name}")
                    return
                elif key_name == 'num_enter':
                    self.keyboard_controller.press(Key.enter)
                    self._pressed_keys.add(Key.enter)
                    if self.on_live_input_callback:
                        self.on_live_input_callback("key", f"⌨ {display_name}")
                    return
            
            # Try to parse as special key
            if key_name.startswith("Key."):
                key_attr = key_name.split('.')[1]
                key = getattr(Key, key_attr, None)
                if key:
                    self.keyboard_controller.press(key)
                    self._pressed_keys.add(key)
                    if self.on_live_input_callback:
                        self.on_live_input_callback("key", f"⌨ {display_name}")
                    return
            
            # Regular character
            self.keyboard_controller.press(key_name)
            self._pressed_keys.add(key_name)
            if self.on_live_input_callback:
                self.on_live_input_callback("key", f"⌨ {display_name}")
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
    
    def _get_display_name_for_replay(self, key_name):
        """Get a nice display name for a key during replay."""
        # Numpad display names
        numpad_display = {
            'num_0': 'NUM 0', 'num_1': 'NUM 1', 'num_2': 'NUM 2', 'num_3': 'NUM 3',
            'num_4': 'NUM 4', 'num_5': 'NUM 5', 'num_6': 'NUM 6', 'num_7': 'NUM 7',
            'num_8': 'NUM 8', 'num_9': 'NUM 9', 'num_decimal': 'NUM .',
            'num_add': 'NUM +', 'num_subtract': 'NUM -',
            'num_multiply': 'NUM *', 'num_divide': 'NUM /',
            'num_enter': 'NUM ENTER',
        }
        
        if key_name in numpad_display:
            return numpad_display[key_name]
        
        if key_name.startswith("Key."):
            display = key_name.replace("Key.", "").upper()
            # Make display names more readable
            replacements = {
                'SPACE': 'SPACE', 'ENTER': 'ENTER', 'BACKSPACE': 'BACKSPACE',
                'TAB': 'TAB', 'CAPS_LOCK': 'CAPS', 'SHIFT': 'SHIFT',
                'SHIFT_R': 'R-SHIFT', 'CTRL': 'CTRL', 'CTRL_L': 'L-CTRL',
                'CTRL_R': 'R-CTRL', 'ALT': 'ALT', 'ALT_L': 'L-ALT',
                'ALT_R': 'R-ALT', 'ALT_GR': 'ALT GR', 'UP': '↑', 'DOWN': '↓',
                'LEFT': '←', 'RIGHT': '→', 'DELETE': 'DEL', 'INSERT': 'INS',
                'HOME': 'HOME', 'END': 'END', 'PAGE_UP': 'PG UP', 'PAGE_DOWN': 'PG DN',
            }
            return replacements.get(display, display)
        
        return key_name
    
    def _replay_key_release(self, event):
        """Replay a keyboard key release event."""
        key_name = event['key']
        
        try:
            # Handle numpad keys
            if key_name.startswith('num_'):
                numpad_chars = {
                    'num_0': '0', 'num_1': '1', 'num_2': '2', 'num_3': '3',
                    'num_4': '4', 'num_5': '5', 'num_6': '6', 'num_7': '7',
                    'num_8': '8', 'num_9': '9', 'num_decimal': '.',
                    'num_add': '+', 'num_subtract': '-',
                    'num_multiply': '*', 'num_divide': '/',
                }
                if key_name in numpad_chars:
                    char = numpad_chars[key_name]
                    self.keyboard_controller.release(char)
                    self._pressed_keys.discard(char)
                    return
                elif key_name == 'num_enter':
                    self.keyboard_controller.release(Key.enter)
                    self._pressed_keys.discard(Key.enter)
                    return
            
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
