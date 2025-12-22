"""Hotkey management functionality."""

from pynput import keyboard
from utils.key_utils import KeyInfo, get_key_info, keys_match, parse_key_name as parse_key, get_display_name

# Debug logging
DEBUG_HOTKEYS = False

def debug_log(msg):
    if DEBUG_HOTKEYS:
        print(f"[HOTKEY DEBUG] {msg}")


class HotkeyManager:
    """Manages hotkey configuration and listening."""
    
    def __init__(self):
        # Default hotkeys - store as KeyInfo normalized tuples
        self.hotkey_record = get_key_info(keyboard.Key.f1)
        self.hotkey_play = get_key_info(keyboard.Key.f2)
        self.hotkey_stop = get_key_info(keyboard.Key.esc)
        self.hotkey_spam = get_key_info(keyboard.Key.f3)
        
        # Hotkey listener
        self.hotkey_listener = None
        
        # Capturing state
        self.capturing_hotkey = None
        
        # Callbacks
        self.on_record_callback = None
        self.on_play_callback = None
        self.on_stop_callback = None
        self.on_spam_callback = None
        self.on_hotkey_captured_callback = None
        self.on_status_callback = None
    
    def set_callbacks(self, on_record=None, on_play=None, on_stop=None, on_spam=None, 
                     on_hotkey_captured=None, on_status=None):
        """Set callback functions for hotkey events."""
        if on_record:
            self.on_record_callback = on_record
        if on_play:
            self.on_play_callback = on_play
        if on_stop:
            self.on_stop_callback = on_stop
        if on_spam:
            self.on_spam_callback = on_spam
        if on_hotkey_captured:
            self.on_hotkey_captured_callback = on_hotkey_captured
        if on_status:
            self.on_status_callback = on_status
    
    def get_key_name(self, key):
        """Get a readable name for a key.
        
        Args:
            key: Can be a pynput key, KeyInfo object, LoadedKeyInfo, or normalized tuple
        """
        # Check for display_name attribute first (works for both KeyInfo and LoadedKeyInfo)
        if hasattr(key, 'display_name'):
            return key.display_name
        elif isinstance(key, tuple):
            return get_display_name(key)
        else:
            # Raw pynput key
            info = get_key_info(key)
            return info.display_name
    
    def parse_key_name(self, key_name):
        """Parse a key name string back to a normalized key tuple."""
        return parse_key(key_name)
    
    def start_capture(self, hotkey_type):
        """Start capturing a new hotkey."""
        self.capturing_hotkey = hotkey_type
        
        if self.on_status_callback:
            self.on_status_callback("Press a key to set as hotkey...", "blue")
    
    def set_hotkey(self, key, hotkey_type):
        """Set a new hotkey."""
        # Get KeyInfo for the pressed key
        key_info = get_key_info(key)
        debug_log(f"set_hotkey called: key={repr(key)}, type={hotkey_type}")
        debug_log(f"  KeyInfo: {key_info}")
        
        if hotkey_type == 'record':
            self.hotkey_record = key_info
        elif hotkey_type == 'play':
            self.hotkey_play = key_info
        elif hotkey_type == 'stop':
            self.hotkey_stop = key_info
        elif hotkey_type == 'spam':
            self.hotkey_spam = key_info
        
        self.capturing_hotkey = None
        
        debug_log(f"  Hotkeys now: record={self.hotkey_record}, play={self.hotkey_play}, stop={self.hotkey_stop}, spam={self.hotkey_spam}")
        
        if self.on_status_callback:
            self.on_status_callback(f"Hotkey updated to {key_info.display_name}", "green")
        
        if self.on_hotkey_captured_callback:
            self.on_hotkey_captured_callback(hotkey_type, key_info)
        
        # Restart hotkey listener with new keys
        self.setup_listener()
    
    def setup_listener(self):
        """Setup the hotkey listener."""
        debug_log("setup_listener called")
        
        # Stop existing listener if any
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            debug_log("  Stopped existing listener")
        
        def on_press(key):
            try:
                debug_log(f"on_press: key={repr(key)}")
                
                # If capturing a hotkey, set it
                if self.capturing_hotkey:
                    debug_log(f"  Capturing mode active for: {self.capturing_hotkey}")
                    self.set_hotkey(key, self.capturing_hotkey)
                    return
                
                # Get KeyInfo for the pressed key
                pressed_key_info = get_key_info(key)
                debug_log(f"  pressed_key_info={pressed_key_info}")
                debug_log(f"  Comparing to: record={self.hotkey_record}, play={self.hotkey_play}, stop={self.hotkey_stop}, spam={self.hotkey_spam}")
                
                # Normal hotkey handling - compare KeyInfo objects
                if pressed_key_info == self.hotkey_record:
                    debug_log("  -> MATCHED record hotkey!")
                    if self.on_record_callback:
                        self.on_record_callback()
                elif pressed_key_info == self.hotkey_play:
                    debug_log("  -> MATCHED play hotkey!")
                    if self.on_play_callback:
                        self.on_play_callback()
                elif pressed_key_info == self.hotkey_stop:
                    debug_log("  -> MATCHED stop hotkey!")
                    if self.on_stop_callback:
                        self.on_stop_callback()
                elif pressed_key_info == self.hotkey_spam:
                    debug_log("  -> MATCHED spam hotkey!")
                    if self.on_spam_callback:
                        self.on_spam_callback()
                else:
                    debug_log("  -> No match")
            except Exception as e:
                debug_log(f"  ERROR in on_press: {e}")
                import traceback
                traceback.print_exc()
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
        debug_log("  New listener started")
    
    def stop_listener(self):
        """Stop the hotkey listener."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
    
    def get_hotkeys(self):
        """Get all configured hotkeys as display names for saving."""
        return {
            'record': self.hotkey_record.display_name if isinstance(self.hotkey_record, KeyInfo) else self.get_key_name(self.hotkey_record),
            'play': self.hotkey_play.display_name if isinstance(self.hotkey_play, KeyInfo) else self.get_key_name(self.hotkey_play),
            'stop': self.hotkey_stop.display_name if isinstance(self.hotkey_stop, KeyInfo) else self.get_key_name(self.hotkey_stop),
            'spam': self.hotkey_spam.display_name if isinstance(self.hotkey_spam, KeyInfo) else self.get_key_name(self.hotkey_spam)
        }
    
    def set_hotkeys(self, hotkeys_dict):
        """Set hotkeys from a dictionary (loading from config)."""
        debug_log(f"set_hotkeys called with: {hotkeys_dict}")
        debug_log(f"  Type of hotkeys_dict: {type(hotkeys_dict)}")
        
        if 'record' in hotkeys_dict:
            debug_log(f"  Processing 'record' key: {hotkeys_dict['record']}")
            normalized = self.parse_key_name(hotkeys_dict['record'])
            debug_log(f"    Normalized tuple: {normalized}")
            # Create a KeyInfo-like object for comparison
            self.hotkey_record = self._create_key_info_from_normalized(normalized, hotkeys_dict['record'])
            debug_log(f"    Created KeyInfo: {self.hotkey_record}")
        if 'play' in hotkeys_dict:
            debug_log(f"  Processing 'play' key: {hotkeys_dict['play']}")
            normalized = self.parse_key_name(hotkeys_dict['play'])
            debug_log(f"    Normalized tuple: {normalized}")
            self.hotkey_play = self._create_key_info_from_normalized(normalized, hotkeys_dict['play'])
            debug_log(f"    Created KeyInfo: {self.hotkey_play}")
        if 'stop' in hotkeys_dict:
            debug_log(f"  Processing 'stop' key: {hotkeys_dict['stop']}")
            normalized = self.parse_key_name(hotkeys_dict['stop'])
            debug_log(f"    Normalized tuple: {normalized}")
            self.hotkey_stop = self._create_key_info_from_normalized(normalized, hotkeys_dict['stop'])
            debug_log(f"    Created KeyInfo: {self.hotkey_stop}")
        if 'spam' in hotkeys_dict:
            debug_log(f"  Processing 'spam' key: {hotkeys_dict['spam']}")
            normalized = self.parse_key_name(hotkeys_dict['spam'])
            debug_log(f"    Normalized tuple: {normalized}")
            self.hotkey_spam = self._create_key_info_from_normalized(normalized, hotkeys_dict['spam'])
            debug_log(f"    Created KeyInfo: {self.hotkey_spam}")
        
        debug_log(f"  Hotkeys loaded: record={self.hotkey_record}, play={self.hotkey_play}, stop={self.hotkey_stop}, spam={self.hotkey_spam}")
        
        # Restart listener with new hotkeys
        self.setup_listener()
    
    def _create_key_info_from_normalized(self, normalized_tuple, display_name):
        """Create a KeyInfo-compatible object from a normalized tuple."""
        # Create a simple object that has the same interface as KeyInfo for comparison
        class LoadedKeyInfo:
            def __init__(self, normalized, display):
                self.normalized_key = normalized
                self.display_name = display
                self.key_name = display
                self.is_numpad = normalized[0] in ('numpad', 'numpad_char')
            
            def __eq__(self, other):
                debug_log(f"      LoadedKeyInfo.__eq__ called: self.normalized_key={self.normalized_key}, other={other}")
                if hasattr(other, 'normalized_key'):
                    debug_log(f"        other.normalized_key={other.normalized_key}")
                    result = self.normalized_key == other.normalized_key
                    debug_log(f"        Comparison result: {result}")
                    return result
                debug_log(f"        other has no normalized_key attribute")
                return False
            
            def __repr__(self):
                return f"LoadedKeyInfo(normalized={self.normalized_key}, display={self.display_name})"
        
        return LoadedKeyInfo(normalized_tuple, display_name)
    
    def get_ignored_keys(self):
        """Get list of hotkeys that should be ignored during recording.
        
        Returns KeyInfo objects that can be compared with incoming key events.
        """
        return [self.hotkey_record, self.hotkey_play, self.hotkey_stop, self.hotkey_spam]
