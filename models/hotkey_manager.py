"""Hotkey management functionality."""

from pynput import keyboard

# Debug logging
DEBUG_HOTKEYS = True

def debug_log(msg):
    if DEBUG_HOTKEYS:
        print(f"[HOTKEY DEBUG] {msg}")


class HotkeyManager:
    """Manages hotkey configuration and listening."""
    
    def __init__(self):
        # Default hotkeys
        self.hotkey_record = keyboard.Key.f1
        self.hotkey_play = keyboard.Key.f2
        self.hotkey_stop = keyboard.Key.esc
        self.hotkey_spam = keyboard.Key.f3
        
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
    
    def _normalize_key(self, key):
        """Normalize a key to lowercase for consistent comparison.
        
        Character keys are case-sensitive in pynput, but users expect
        hotkeys to work regardless of shift/caps lock state.
        """
        if hasattr(key, 'char') and key.char is not None:
            # For character keys, normalize to lowercase
            return keyboard.KeyCode.from_char(key.char.lower())
        return key
    
    def get_key_name(self, key):
        """Get a readable name for a key."""
        if hasattr(key, 'name'):
            return key.name.upper()
        # For KeyCode (character keys), strip quotes from string representation
        return str(key).replace('Key.', '').strip("'\"").upper()
    
    def parse_key_name(self, key_name):
        """Parse a key name string back to a keyboard Key object."""
        # Strip any quotes that might be present
        key_name_clean = key_name.strip("'\"")
        key_name_upper = key_name_clean.upper()
        
        # Try to match keyboard.Key attributes (special keys like F1, ESC, etc.)
        for attr_name in dir(keyboard.Key):
            if not attr_name.startswith('_'):
                attr = getattr(keyboard.Key, attr_name)
                if hasattr(attr, 'name') and attr.name.upper() == key_name_upper:
                    return attr
        
        # If not found in keyboard.Key, try as KeyCode (character key)
        try:
            # Use the cleaned key name (single character)
            char = key_name_clean.lower() if len(key_name_clean) == 1 else key_name_clean[0].lower()
            return keyboard.KeyCode.from_char(char)
        except:
            # Default to F1 if parsing fails
            return keyboard.Key.f1
    
    def start_capture(self, hotkey_type):
        """Start capturing a new hotkey."""
        self.capturing_hotkey = hotkey_type
        
        if self.on_status_callback:
            self.on_status_callback("Press a key to set as hotkey...", "blue")
    
    def set_hotkey(self, key, hotkey_type):
        """Set a new hotkey."""
        debug_log(f"set_hotkey called: key={repr(key)}, type={hotkey_type}")
        
        # Normalize character keys to lowercase for consistent comparison
        normalized_key = self._normalize_key(key)
        debug_log(f"  normalized_key={repr(normalized_key)}")
        
        if hotkey_type == 'record':
            self.hotkey_record = normalized_key
        elif hotkey_type == 'play':
            self.hotkey_play = normalized_key
        elif hotkey_type == 'stop':
            self.hotkey_stop = normalized_key
        elif hotkey_type == 'spam':
            self.hotkey_spam = normalized_key
        
        self.capturing_hotkey = None
        
        debug_log(f"  Hotkeys now: record={repr(self.hotkey_record)}, play={repr(self.hotkey_play)}, stop={repr(self.hotkey_stop)}, spam={repr(self.hotkey_spam)}")
        
        if self.on_status_callback:
            self.on_status_callback(f"Hotkey updated to {self.get_key_name(key)}", "green")
        
        if self.on_hotkey_captured_callback:
            self.on_hotkey_captured_callback(hotkey_type, key)
        
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
                
                # Normalize the pressed key for case-insensitive comparison
                normalized_key = self._normalize_key(key)
                debug_log(f"  normalized_key={repr(normalized_key)}")
                debug_log(f"  Comparing to: record={repr(self.hotkey_record)}, play={repr(self.hotkey_play)}, stop={repr(self.hotkey_stop)}, spam={repr(self.hotkey_spam)}")
                
                # Normal hotkey handling
                if normalized_key == self.hotkey_record:
                    debug_log("  -> MATCHED record hotkey!")
                    if self.on_record_callback:
                        self.on_record_callback()
                elif normalized_key == self.hotkey_play:
                    debug_log("  -> MATCHED play hotkey!")
                    if self.on_play_callback:
                        self.on_play_callback()
                elif normalized_key == self.hotkey_stop:
                    debug_log("  -> MATCHED stop hotkey!")
                    if self.on_stop_callback:
                        self.on_stop_callback()
                elif normalized_key == self.hotkey_spam:
                    debug_log("  -> MATCHED spam hotkey!")
                    if self.on_spam_callback:
                        self.on_spam_callback()
                else:
                    debug_log("  -> No match")
            except Exception as e:
                debug_log(f"  ERROR in on_press: {e}")
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
        debug_log("  New listener started")
    
    def stop_listener(self):
        """Stop the hotkey listener."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
    
    def get_hotkeys(self):
        """Get all configured hotkeys."""
        return {
            'record': self.get_key_name(self.hotkey_record),
            'play': self.get_key_name(self.hotkey_play),
            'stop': self.get_key_name(self.hotkey_stop),
            'spam': self.get_key_name(self.hotkey_spam)
        }
    
    def set_hotkeys(self, hotkeys_dict):
        """Set hotkeys from a dictionary."""
        if 'record' in hotkeys_dict:
            self.hotkey_record = self.parse_key_name(hotkeys_dict['record'])
        if 'play' in hotkeys_dict:
            self.hotkey_play = self.parse_key_name(hotkeys_dict['play'])
        if 'stop' in hotkeys_dict:
            self.hotkey_stop = self.parse_key_name(hotkeys_dict['stop'])
        if 'spam' in hotkeys_dict:
            self.hotkey_spam = self.parse_key_name(hotkeys_dict['spam'])
        
        # Restart listener with new hotkeys
        self.setup_listener()
    
    def get_ignored_keys(self):
        """Get list of hotkeys that should be ignored during recording."""
        return [self.hotkey_record, self.hotkey_play, self.hotkey_stop, self.hotkey_spam]
