"""Hotkey management functionality."""

from pynput import keyboard


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
    
    def get_key_name(self, key):
        """Get a readable name for a key."""
        if hasattr(key, 'name'):
            return key.name.upper()
        return str(key).replace('Key.', '').upper()
    
    def parse_key_name(self, key_name):
        """Parse a key name string back to a keyboard Key object."""
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
    
    def start_capture(self, hotkey_type):
        """Start capturing a new hotkey."""
        self.capturing_hotkey = hotkey_type
        
        if self.on_status_callback:
            self.on_status_callback("Press a key to set as hotkey...", "blue")
    
    def set_hotkey(self, key, hotkey_type):
        """Set a new hotkey."""
        if hotkey_type == 'record':
            self.hotkey_record = key
        elif hotkey_type == 'play':
            self.hotkey_play = key
        elif hotkey_type == 'stop':
            self.hotkey_stop = key
        elif hotkey_type == 'spam':
            self.hotkey_spam = key
        
        self.capturing_hotkey = None
        
        if self.on_status_callback:
            self.on_status_callback(f"Hotkey updated to {self.get_key_name(key)}", "green")
        
        if self.on_hotkey_captured_callback:
            self.on_hotkey_captured_callback(hotkey_type, key)
        
        # Restart hotkey listener with new keys
        self.setup_listener()
    
    def setup_listener(self):
        """Setup the hotkey listener."""
        # Stop existing listener if any
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        def on_press(key):
            try:
                # If capturing a hotkey, set it
                if self.capturing_hotkey:
                    self.set_hotkey(key, self.capturing_hotkey)
                    return
                
                # Normal hotkey handling
                if key == self.hotkey_record:
                    if self.on_record_callback:
                        self.on_record_callback()
                elif key == self.hotkey_play:
                    if self.on_play_callback:
                        self.on_play_callback()
                elif key == self.hotkey_stop:
                    if self.on_stop_callback:
                        self.on_stop_callback()
                elif key == self.hotkey_spam:
                    if self.on_spam_callback:
                        self.on_spam_callback()
            except:
                pass
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
    
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
