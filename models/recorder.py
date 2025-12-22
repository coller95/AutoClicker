"""Event recording functionality - captures mouse and keyboard events."""

from pynput import mouse, keyboard
import time
from typing import List, Callable, Optional, Any

from utils.key_utils import get_key_info


class Recorder:
    """Records mouse and keyboard events."""
    
    def __init__(self):
        # Recording state
        self.is_recording = False
        self.recorded_events: List[dict] = []
        self.start_time: Optional[float] = None
        
        # Listeners
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        
        # Keys to ignore during recording (e.g., hotkeys)
        self._ignored_keys: List[Any] = []
        
        # Callbacks
        self._on_event: Optional[Callable[[str], None]] = None
        self._on_status: Optional[Callable[[str, str], None]] = None
        self._on_live_input: Optional[Callable[[str, str], None]] = None
    
    def set_callbacks(
        self,
        on_event: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[str, str], None]] = None,
        on_live_input: Optional[Callable[[str, str], None]] = None
    ):
        """Set callback functions for recording events."""
        if on_event:
            self._on_event = on_event
        if on_status:
            self._on_status = on_status
        if on_live_input:
            self._on_live_input = on_live_input
    
    def set_ignored_keys(self, keys: List[Any]):
        """Set keys to ignore during recording (e.g., hotkeys)."""
        self._ignored_keys = keys
    
    def start(self) -> bool:
        """Start recording mouse and keyboard events.
        
        Returns:
            True if recording started successfully, False otherwise.
        """
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        
        # Start mouse listener
        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move
        )
        self._mouse_listener.start()
        
        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._keyboard_listener.start()
        
        if self._on_status:
            self._on_status("Recording... Click and type!", "red")
        
        return True
    
    def stop(self) -> int:
        """Stop recording events.
        
        Returns:
            Number of events recorded.
        """
        self.is_recording = False
        
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        
        event_count = len(self.recorded_events)
        
        if self._on_status:
            self._on_status(f"Recording stopped. {event_count} events recorded.", "green")
        
        return event_count
    
    def clear(self):
        """Clear all recorded events."""
        self.recorded_events = []
        if self._on_status:
            self._on_status("Recording cleared!", "green")
    
    def get_events(self) -> List[dict]:
        """Get the list of recorded events."""
        return self.recorded_events
    
    def set_events(self, events: List[dict]):
        """Set the list of recorded events (e.g., from loaded file)."""
        self.recorded_events = events
    
    @property
    def event_count(self) -> int:
        """Get the number of recorded events."""
        return len(self.recorded_events)
    
    # -------------------------------------------------------------------------
    # Private: Event handlers
    # -------------------------------------------------------------------------
    
    def _is_ignored_key(self, key) -> bool:
        """Check if a key should be ignored during recording."""
        key_info = get_key_info(key)
        for ignored in self._ignored_keys:
            if hasattr(ignored, 'normalized_key'):
                if key_info.normalized_key == ignored.normalized_key:
                    return True
            elif ignored == key:
                return True
        return False
    
    def _on_click(self, x: int, y: int, button, pressed: bool):
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
        
        if self._on_event:
            log_text = f"[{timestamp:.2f}s] Mouse {action}: {button} at ({x}, {y})\n"
            self._on_event(log_text)
        
        if self._on_live_input and pressed:
            self._on_live_input("mouse", f"🖱 {button_name} ({x}, {y})")
    
    def _on_move(self, x: int, y: int):
        """Handle mouse move events (currently not recorded)."""
        pass
    
    def _on_key_press(self, key):
        """Handle keyboard key press events."""
        if not self.is_recording:
            return
        
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
        
        if self._on_event:
            log_text = f"[{timestamp:.2f}s] Key Press: {key_name}\n"
            self._on_event(log_text)
        
        if self._on_live_input:
            self._on_live_input("key", f"⌨ {display_name}")
    
    def _on_key_release(self, key):
        """Handle keyboard key release events."""
        if not self.is_recording:
            return
        
        if self._is_ignored_key(key):
            return
        
        timestamp = time.time() - self.start_time
        key_name, _ = self._get_key_names(key)
        
        event = {
            'type': 'key_release',
            'key': key_name,
            'timestamp': timestamp
        }
        self.recorded_events.append(event)
        
        if self._on_event:
            log_text = f"[{timestamp:.2f}s] Key Release: {key_name}\n"
            self._on_event(log_text)
    
    def _get_key_names(self, key) -> tuple:
        """Get key name and display name for a key.
        
        Returns:
            tuple: (key_name for recording, display_name for UI)
        """
        # Use centralized key_utils for consistent identification
        key_info = get_key_info(key)
        return (key_info.key_name, key_info.display_name)
