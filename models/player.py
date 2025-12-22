"""Event playback functionality - replays recorded mouse and keyboard events."""

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading
import time
from typing import List, Callable, Optional, Set

from utils.constants import Defaults


class Player:
    """Plays back recorded mouse and keyboard events."""
    
    def __init__(self):
        # Controllers
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        
        # Playback state
        self.is_playing = False
        self._playback_thread: Optional[threading.Thread] = None
        
        # Track pressed buttons/keys for cleanup
        self._pressed_mouse_buttons: Set[Button] = set()
        self._pressed_keys: Set = set()
        
        # Callbacks
        self._on_status: Optional[Callable[[str, str], None]] = None
        self._on_complete: Optional[Callable[[], None]] = None
        self._on_live_input: Optional[Callable[[str, str], None]] = None
        self._on_countdown: Optional[Callable[[float], None]] = None
    
    def set_callbacks(
        self,
        on_status: Optional[Callable[[str, str], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
        on_live_input: Optional[Callable[[str, str], None]] = None,
        on_countdown: Optional[Callable[[float], None]] = None
    ):
        """Set callback functions for playback events."""
        if on_status:
            self._on_status = on_status
        if on_complete:
            self._on_complete = on_complete
        if on_live_input:
            self._on_live_input = on_live_input
        if on_countdown:
            self._on_countdown = on_countdown
    
    def start(
        self,
        events: List[dict],
        loop_count: int = 1,
        loop_delay: float = 0.0,
        playback_speed: float = 1.0
    ) -> bool:
        """Start playing back recorded events.
        
        Args:
            events: List of recorded events to play back.
            loop_count: Number of times to loop (0 = infinite).
            loop_delay: Delay between loops in seconds.
            playback_speed: Speed multiplier for playback.
            
        Returns:
            True if playback started successfully, False otherwise.
        """
        if not events:
            if self._on_status:
                self._on_status("No events to play!", "red")
            return False
        
        if self.is_playing:
            return False
        
        self.is_playing = True
        
        if self._on_status:
            if loop_count == 0:
                self._on_status("Playing recording (Infinite loops)...", "blue")
            else:
                self._on_status(f"Playing recording ({loop_count} loops)...", "blue")
        
        # Start playback in a separate thread
        self._playback_thread = threading.Thread(
            target=self._playback_worker,
            args=(events, loop_count, loop_delay, playback_speed)
        )
        self._playback_thread.daemon = True
        self._playback_thread.start()
        
        return True
    
    def stop(self) -> bool:
        """Stop playing back events.
        
        Returns:
            True if playback was stopped, False if not playing.
        """
        if not self.is_playing:
            return False
        
        self.is_playing = False
        self._release_all_pressed()
        
        if self._on_status:
            self._on_status("Playback stopped!", "orange")
        
        return True
    
    # -------------------------------------------------------------------------
    # Private: Playback worker
    # -------------------------------------------------------------------------
    
    def _playback_worker(
        self,
        events: List[dict],
        loop_count: int,
        loop_delay: float,
        playback_speed: float
    ):
        """Worker thread for playing back events."""
        self._pressed_mouse_buttons.clear()
        self._pressed_keys.clear()
        
        try:
            loop = 0
            while True:
                if not self.is_playing:
                    break
                
                # Check loop limit
                if loop_count > 0 and loop >= loop_count:
                    break
                
                # Delay between loops (not before first loop)
                if loop > 0 and loop_delay > 0:
                    self._wait_with_countdown(loop_delay)
                
                loop += 1
                
                if self._on_status:
                    if loop_count == 0:
                        self._on_status(f"Playing loop {loop} (Infinite)...", "blue")
                    else:
                        self._on_status(f"Playing loop {loop}/{loop_count}...", "blue")
                
                # Play all events
                last_timestamp = 0
                for event in events:
                    if not self.is_playing:
                        break
                    
                    # Wait for appropriate time
                    wait_time = event['timestamp'] - last_timestamp
                    if wait_time > 0:
                        adjusted_wait = wait_time / playback_speed if playback_speed > 0 else wait_time
                        time.sleep(adjusted_wait)
                    last_timestamp = event['timestamp']
                    
                    # Execute event
                    self._execute_event(event)
        
        except Exception as e:
            if self._on_status:
                self._on_status(f"Error: {str(e)}", "red")
        
        finally:
            self._release_all_pressed()
            self.is_playing = False
            if self._on_complete:
                self._on_complete()
            if self._on_status:
                self._on_status("Playback completed!", "green")
    
    def _wait_with_countdown(self, delay: float):
        """Wait with countdown updates."""
        remaining = delay
        while remaining > 0 and self.is_playing:
            if self._on_countdown:
                self._on_countdown(remaining)
            sleep_time = min(0.1, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time
        
        if self._on_countdown and self.is_playing:
            self._on_countdown(0)
    
    def _execute_event(self, event: dict):
        """Execute a single event."""
        event_type = event['type']
        
        if event_type == 'mouse_click':
            self._replay_mouse_click(event)
        elif event_type == 'key_press':
            self._replay_key_press(event)
        elif event_type == 'key_release':
            self._replay_key_release(event)
    
    # -------------------------------------------------------------------------
    # Private: Event replay
    # -------------------------------------------------------------------------
    
    def _replay_mouse_click(self, event: dict):
        """Replay a mouse click event."""
        x, y = event['x'], event['y']
        button_str = event['button']
        pressed = event['pressed']
        
        # Move mouse
        self._mouse.position = (x, y)
        
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
        
        # Live input callback
        if self._on_live_input and pressed:
            self._on_live_input("mouse", f"🖱 {button_name} ({x}, {y})")
        
        # Press or release
        if pressed:
            self._mouse.press(button)
            self._pressed_mouse_buttons.add(button)
        else:
            self._mouse.release(button)
            self._pressed_mouse_buttons.discard(button)
    
    def _replay_key_press(self, event: dict):
        """Replay a keyboard key press event."""
        key_name = event['key']
        display_name = self._get_display_name(key_name)
        
        try:
            key = self._parse_key(key_name)
            if key is not None:
                self._keyboard.press(key)
                self._pressed_keys.add(key)
                
                if self._on_live_input:
                    self._on_live_input("key", f"⌨ {display_name}")
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
    
    def _replay_key_release(self, event: dict):
        """Replay a keyboard key release event."""
        key_name = event['key']
        
        try:
            key = self._parse_key(key_name)
            if key is not None:
                self._keyboard.release(key)
                self._pressed_keys.discard(key)
        except Exception as e:
            print(f"Error releasing key {key_name}: {e}")
    
    def _parse_key(self, key_name: str):
        """Parse a key name to a pynput key."""
        # Numpad keys
        numpad_chars = {
            'num_0': '0', 'num_1': '1', 'num_2': '2', 'num_3': '3',
            'num_4': '4', 'num_5': '5', 'num_6': '6', 'num_7': '7',
            'num_8': '8', 'num_9': '9', 'num_decimal': '.',
            'num_add': '+', 'num_subtract': '-',
            'num_multiply': '*', 'num_divide': '/',
        }
        
        if key_name in numpad_chars:
            return numpad_chars[key_name]
        
        if key_name == 'num_enter':
            return Key.enter
        
        # Special keys
        if key_name.startswith("Key."):
            key_attr = key_name.split('.')[1]
            return getattr(Key, key_attr, None)
        
        # Regular character
        return key_name
    
    def _get_display_name(self, key_name: str) -> str:
        """Get a display name for a key."""
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
            display_map = {
                'SPACE': 'SPACE', 'ENTER': 'ENTER', 'BACKSPACE': 'BACKSPACE',
                'TAB': 'TAB', 'CAPS_LOCK': 'CAPS', 'SHIFT': 'SHIFT',
                'SHIFT_R': 'R-SHIFT', 'CTRL': 'CTRL', 'CTRL_L': 'L-CTRL',
                'CTRL_R': 'R-CTRL', 'ALT': 'ALT', 'ALT_L': 'L-ALT',
                'ALT_R': 'R-ALT', 'ALT_GR': 'ALT GR', 'UP': '↑', 'DOWN': '↓',
                'LEFT': '←', 'RIGHT': '→', 'DELETE': 'DEL', 'INSERT': 'INS',
                'HOME': 'HOME', 'END': 'END', 'PAGE_UP': 'PG UP', 'PAGE_DOWN': 'PG DN',
            }
            return display_map.get(display, display)
        
        return key_name
    
    def _release_all_pressed(self):
        """Release all pressed mouse buttons and keyboard keys."""
        for button in list(self._pressed_mouse_buttons):
            try:
                self._mouse.release(button)
            except Exception:
                pass
        self._pressed_mouse_buttons.clear()
        
        for key in list(self._pressed_keys):
            try:
                self._keyboard.release(key)
            except Exception:
                pass
        self._pressed_keys.clear()
