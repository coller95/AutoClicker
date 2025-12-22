"""Utility module for handling keyboard key differentiation.

This module provides consistent handling of numpad vs regular keys across
the application. On Linux/X11, numpad keys can be differentiated from regular
keys by their keysym values. On Windows, virtual key codes (VK) are used.
"""

import os
import sys
from pynput import keyboard

# Debug logging
DEBUG_KEYS = False


def detect_environment():
    """
    Detect the current environment/platform.
    
    Returns:
        str: 'windows', 'x11', 'wayland', or 'unknown'
    """
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    elif sys.platform.startswith('linux'):
        # Check for Wayland vs X11
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        if session_type == 'wayland':
            return 'wayland'
        elif session_type == 'x11':
            return 'x11'
        # Fallback: check WAYLAND_DISPLAY and DISPLAY
        if os.environ.get('WAYLAND_DISPLAY'):
            return 'wayland'
        if os.environ.get('DISPLAY'):
            return 'x11'
        return 'linux_unknown'
    return 'unknown'


# Current environment
CURRENT_ENV = detect_environment()


def get_environment():
    """
    Get the current environment/platform.
    
    Returns:
        str: 'windows', 'x11', 'wayland', 'macos', or 'unknown'
    """
    return CURRENT_ENV


def is_numpad_supported():
    """
    Check if numpad differentiation is supported on the current platform.
    
    Returns:
        bool: True if numpad keys can be differentiated from regular keys
    """
    return CURRENT_ENV in ('windows', 'x11', 'linux_unknown')


def debug_log(msg):
    if DEBUG_KEYS:
        print(f"[KEY_UTILS DEBUG] {msg}")


# Windows numpad virtual key codes
WINDOWS_NUMPAD_VK = {
    96:  ('num_0', 'NUM 0'),       # VK_NUMPAD0
    97:  ('num_1', 'NUM 1'),       # VK_NUMPAD1
    98:  ('num_2', 'NUM 2'),       # VK_NUMPAD2
    99:  ('num_3', 'NUM 3'),       # VK_NUMPAD3
    100: ('num_4', 'NUM 4'),       # VK_NUMPAD4
    101: ('num_5', 'NUM 5'),       # VK_NUMPAD5
    102: ('num_6', 'NUM 6'),       # VK_NUMPAD6
    103: ('num_7', 'NUM 7'),       # VK_NUMPAD7
    104: ('num_8', 'NUM 8'),       # VK_NUMPAD8
    105: ('num_9', 'NUM 9'),       # VK_NUMPAD9
    110: ('num_decimal', 'NUM .'), # VK_DECIMAL
    107: ('num_add', 'NUM +'),     # VK_ADD
    109: ('num_subtract', 'NUM -'), # VK_SUBTRACT
    106: ('num_multiply', 'NUM *'), # VK_MULTIPLY
    111: ('num_divide', 'NUM /'),   # VK_DIVIDE
    # Note: VK_RETURN (13) is shared between Enter and Numpad Enter
    # On Windows, distinguishing them requires scan code checking
}

# Reverse mapping for Windows: key name -> VK code
WINDOWS_NUMPAD_NAME_TO_VK = {name: vk for vk, (name, _) in WINDOWS_NUMPAD_VK.items()}


# X11 numpad keysyms - these are the raw keysym values for numpad keys
X11_NUMPAD_KEYSYMS = {
    65437: ('num_5', 'NUM 5'),       # KP_5 / KP_Begin
    65436: ('num_4', 'NUM 4'),       # KP_4 / KP_Left
    65438: ('num_6', 'NUM 6'),       # KP_6 / KP_Right
    65432: ('num_8', 'NUM 8'),       # KP_8 / KP_Up
    65433: ('num_2', 'NUM 2'),       # KP_2 / KP_Down
    65434: ('num_9', 'NUM 9'),       # KP_9 / KP_Prior
    65435: ('num_3', 'NUM 3'),       # KP_3 / KP_Next
    65429: ('num_7', 'NUM 7'),       # KP_7 / KP_Home
    65430: ('num_1', 'NUM 1'),       # KP_1 / KP_End
    65456: ('num_0', 'NUM 0'),       # KP_0 / KP_Insert
    65439: ('num_decimal', 'NUM .'), # KP_Decimal / KP_Delete
    65451: ('num_add', 'NUM +'),     # KP_Add
    65453: ('num_subtract', 'NUM -'), # KP_Subtract
    65450: ('num_multiply', 'NUM *'), # KP_Multiply
    65455: ('num_divide', 'NUM /'),   # KP_Divide
    65421: ('num_enter', 'NUM ENTER'), # KP_Enter
}

# Reverse mapping: key name -> keysym
NUMPAD_NAME_TO_KEYSYM = {name: keysym for keysym, (name, _) in X11_NUMPAD_KEYSYMS.items()}


class KeyInfo:
    """Information about a key press, including numpad differentiation."""
    
    def __init__(self, key):
        """
        Initialize KeyInfo from a pynput key.
        
        Args:
            key: pynput keyboard key object
        """
        self.original_key = key
        self.is_numpad = False
        self.key_name = None
        self.display_name = None
        self.normalized_key = None
        
        self._analyze_key(key)
    
    def _analyze_key(self, key):
        """Analyze the key and determine its properties."""
        key_str = str(key)
        debug_log(f"Analyzing key: {repr(key)}, str={key_str}, env={CURRENT_ENV}")
        
        # Windows: Check VK codes for numpad keys
        if CURRENT_ENV == 'windows':
            vk = getattr(key, 'vk', None)
            debug_log(f"  Windows VK code: {vk}")
            
            if vk is not None and vk in WINDOWS_NUMPAD_VK:
                self.is_numpad = True
                self.key_name, self.display_name = WINDOWS_NUMPAD_VK[vk]
                self.normalized_key = ('numpad_vk', vk)
                debug_log(f"  -> Windows numpad key: {self.key_name}")
                return
        
        # X11/Linux: Check for X11 keysym format: <number>
        if CURRENT_ENV in ('x11', 'linux_unknown'):
            if key_str.startswith('<') and key_str.endswith('>'):
                try:
                    keysym = int(key_str[1:-1])
                    debug_log(f"  X11 keysym detected: {keysym}")
                    
                    if keysym in X11_NUMPAD_KEYSYMS:
                        self.is_numpad = True
                        self.key_name, self.display_name = X11_NUMPAD_KEYSYMS[keysym]
                        # Create a normalized key that preserves numpad identity
                        self.normalized_key = ('numpad', keysym)
                        debug_log(f"  -> Numpad key: {self.key_name}")
                        return
                    else:
                        # Unknown keysym
                        self.key_name = key_str
                        self.display_name = f'KEY {keysym}'
                        self.normalized_key = ('keysym', keysym)
                        debug_log(f"  -> Unknown keysym: {keysym}")
                        return
                except ValueError:
                    pass
        
        # Check for Key.* constants (special keys like num_lock, F1, etc.)
        if hasattr(key, 'name'):
            self.key_name = key.name.upper()
            self.display_name = key.name.upper()
            self.normalized_key = ('special', key)
            debug_log(f"  -> Special key: {self.key_name}")
            return
        
        # Character key - check vk to differentiate numpad
        if hasattr(key, 'char') and key.char is not None:
            char = key.char
            vk = getattr(key, 'vk', None)
            debug_log(f"  Char key: char={repr(char)}, vk={vk}")
            
            # Windows: VK codes already handled above, remaining chars are regular keys
            # X11/Linux: vk=None typically means numpad when NumLock is ON
            if CURRENT_ENV in ('x11', 'linux_unknown') and vk is None:
                # Likely numpad key with NumLock ON
                if char in '0123456789':
                    self.is_numpad = True
                    self.key_name = f'num_{char}'
                    self.display_name = f'NUM {char}'
                    self.normalized_key = ('numpad_char', char)
                    debug_log(f"  -> Numpad digit: {self.key_name}")
                    return
                elif char in '+':
                    self.is_numpad = True
                    self.key_name = 'num_add'
                    self.display_name = 'NUM +'
                    self.normalized_key = ('numpad_char', '+')
                    debug_log(f"  -> Numpad add")
                    return
                elif char == '-':
                    self.is_numpad = True
                    self.key_name = 'num_subtract'
                    self.display_name = 'NUM -'
                    self.normalized_key = ('numpad_char', '-')
                    debug_log(f"  -> Numpad subtract")
                    return
                elif char == '*':
                    self.is_numpad = True
                    self.key_name = 'num_multiply'
                    self.display_name = 'NUM *'
                    self.normalized_key = ('numpad_char', '*')
                    debug_log(f"  -> Numpad multiply")
                    return
                elif char == '/':
                    self.is_numpad = True
                    self.key_name = 'num_divide'
                    self.display_name = 'NUM /'
                    self.normalized_key = ('numpad_char', '/')
                    debug_log(f"  -> Numpad divide")
                    return
                elif char in '.,':
                    self.is_numpad = True
                    self.key_name = 'num_decimal'
                    self.display_name = f'NUM {char}'
                    self.normalized_key = ('numpad_char', 'decimal')
                    debug_log(f"  -> Numpad decimal")
                    return
            
            # Regular character key - normalize to lowercase
            char_lower = char.lower()
            self.key_name = char_lower
            self.display_name = char.upper()
            self.normalized_key = ('char', char_lower)
            debug_log(f"  -> Regular char: {self.key_name}")
            return
        
        # Fallback
        self.key_name = key_str
        self.display_name = key_str
        self.normalized_key = ('unknown', key_str)
        debug_log(f"  -> Unknown key: {key_str}")
    
    def __eq__(self, other):
        """Compare two KeyInfo objects for equality."""
        if hasattr(other, 'normalized_key'):
            return self.normalized_key == other.normalized_key
        return False
    
    def __hash__(self):
        """Make KeyInfo hashable."""
        if isinstance(self.normalized_key, tuple):
            # Handle unhashable types in the tuple
            key_type, key_value = self.normalized_key
            if key_type == 'special':
                return hash((key_type, str(key_value)))
            return hash(self.normalized_key)
        return hash(self.normalized_key)
    
    def __repr__(self):
        return f"KeyInfo(name={self.key_name}, display={self.display_name}, numpad={self.is_numpad}, normalized={self.normalized_key})"


def get_key_info(key):
    """
    Get detailed information about a key press.
    
    Args:
        key: pynput keyboard key object
        
    Returns:
        KeyInfo: Object containing key information
    """
    return KeyInfo(key)


def keys_match(key1, key2):
    """
    Check if two keys match, considering numpad differentiation.
    
    Args:
        key1: First key (pynput key or KeyInfo)
        key2: Second key (pynput key or KeyInfo)
        
    Returns:
        bool: True if keys match
    """
    info1 = key1 if isinstance(key1, KeyInfo) else KeyInfo(key1)
    info2 = key2 if isinstance(key2, KeyInfo) else KeyInfo(key2)
    
    match = info1.normalized_key == info2.normalized_key
    debug_log(f"keys_match: {info1.normalized_key} == {info2.normalized_key} -> {match}")
    return match


def parse_key_name(key_name):
    """
    Parse a key name string back to a normalized key tuple.
    
    This is used when loading hotkeys from config files.
    Returns environment-appropriate normalized keys for cross-platform compatibility.
    
    Args:
        key_name: String name of the key (e.g., 'F1', 'A', 'NUM +', 'num_add')
        
    Returns:
        tuple: Normalized key tuple for comparison
    """
    key_name_clean = key_name.strip("'\"")
    key_name_upper = key_name_clean.upper()
    
    debug_log(f"parse_key_name: {key_name} -> clean={key_name_clean}, upper={key_name_upper}, env={CURRENT_ENV}")
    
    # Check for numpad keys
    if key_name_clean.startswith('num_') or key_name_upper.startswith('NUM '):
        # It's a numpad key - return environment-appropriate normalized key
        name_lower = key_name_clean.lower()
        
        # On Windows, use VK codes
        if CURRENT_ENV == 'windows':
            if name_lower in WINDOWS_NUMPAD_NAME_TO_VK:
                vk = WINDOWS_NUMPAD_NAME_TO_VK[name_lower]
                debug_log(f"  -> Windows numpad VK: {vk}")
                return ('numpad_vk', vk)
        
        # On X11, use keysyms
        if CURRENT_ENV in ('x11', 'linux_unknown'):
            if name_lower in NUMPAD_NAME_TO_KEYSYM:
                keysym = NUMPAD_NAME_TO_KEYSYM[name_lower]
                debug_log(f"  -> X11 numpad keysym: {keysym}")
                return ('numpad', keysym)
        
        # Parse NUM X format - use generic numpad_char for portability
        if key_name_upper.startswith('NUM '):
            suffix = key_name_clean[4:] if key_name_clean.startswith('num_') else key_name_clean[4:]
            debug_log(f"  -> Parsing NUM format, suffix='{suffix}'")
            
            if suffix in '0123456789':
                # On Windows, map to VK if possible
                if CURRENT_ENV == 'windows':
                    vk_name = f'num_{suffix}'
                    if vk_name in WINDOWS_NUMPAD_NAME_TO_VK:
                        return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK[vk_name])
                return ('numpad_char', suffix)
            elif suffix in ['+', 'add', 'ADD']:
                if CURRENT_ENV == 'windows' and 'num_add' in WINDOWS_NUMPAD_NAME_TO_VK:
                    return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK['num_add'])
                return ('numpad_char', '+')
            elif suffix in ['-', 'subtract', 'SUBTRACT']:
                if CURRENT_ENV == 'windows' and 'num_subtract' in WINDOWS_NUMPAD_NAME_TO_VK:
                    return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK['num_subtract'])
                return ('numpad_char', '-')
            elif suffix in ['*', 'multiply', 'MULTIPLY']:
                if CURRENT_ENV == 'windows' and 'num_multiply' in WINDOWS_NUMPAD_NAME_TO_VK:
                    return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK['num_multiply'])
                return ('numpad_char', '*')
            elif suffix in ['/', 'divide', 'DIVIDE']:
                if CURRENT_ENV == 'windows' and 'num_divide' in WINDOWS_NUMPAD_NAME_TO_VK:
                    return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK['num_divide'])
                return ('numpad_char', '/')
            elif suffix in ['.', ',', 'decimal', 'DECIMAL']:
                if CURRENT_ENV == 'windows' and 'num_decimal' in WINDOWS_NUMPAD_NAME_TO_VK:
                    return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK['num_decimal'])
                return ('numpad_char', 'decimal')
            elif suffix.upper() == 'ENTER':
                if CURRENT_ENV in ('x11', 'linux_unknown') and 'num_enter' in NUMPAD_NAME_TO_KEYSYM:
                    return ('numpad', NUMPAD_NAME_TO_KEYSYM['num_enter'])
                # Windows numpad enter is harder to distinguish
        
        # Try direct lookup based on environment
        if CURRENT_ENV == 'windows' and name_lower in WINDOWS_NUMPAD_NAME_TO_VK:
            return ('numpad_vk', WINDOWS_NUMPAD_NAME_TO_VK[name_lower])
        if CURRENT_ENV in ('x11', 'linux_unknown') and name_lower in NUMPAD_NAME_TO_KEYSYM:
            return ('numpad', NUMPAD_NAME_TO_KEYSYM[name_lower])
        
        debug_log(f"  -> Unknown numpad key: {key_name}")
    
    # Check for special keys (F1, ESC, etc.)
    for attr_name in dir(keyboard.Key):
        if not attr_name.startswith('_'):
            attr = getattr(keyboard.Key, attr_name)
            if hasattr(attr, 'name') and attr.name.upper() == key_name_upper:
                debug_log(f"  -> Special key: {attr}")
                return ('special', attr)
    
    # Regular character key - normalize to lowercase
    if len(key_name_clean) == 1:
        char_lower = key_name_clean.lower()
        debug_log(f"  -> Char key: {char_lower}")
        return ('char', char_lower)
    
    # Fallback
    debug_log(f"  -> Unknown: {key_name}")
    return ('unknown', key_name)


def get_display_name(normalized_key):
    """
    Get a display name for a normalized key.
    
    Args:
        normalized_key: Tuple from KeyInfo.normalized_key or parse_key_name
        
    Returns:
        str: Human-readable display name
    """
    if not isinstance(normalized_key, tuple) or len(normalized_key) != 2:
        return str(normalized_key)
    
    key_type, key_value = normalized_key
    
    if key_type == 'numpad':
        if key_value in X11_NUMPAD_KEYSYMS:
            return X11_NUMPAD_KEYSYMS[key_value][1]
        return f'NUM KEY {key_value}'
    
    elif key_type == 'numpad_vk':
        # Windows VK codes
        if key_value in WINDOWS_NUMPAD_VK:
            return WINDOWS_NUMPAD_VK[key_value][1]
        return f'NUM KEY {key_value}'
    
    elif key_type == 'numpad_char':
        if key_value == 'decimal':
            return 'NUM .'
        return f'NUM {key_value}'
    
    elif key_type == 'special':
        if hasattr(key_value, 'name'):
            return key_value.name.upper()
        return str(key_value).upper()
    
    elif key_type == 'char':
        return key_value.upper()
    
    elif key_type == 'keysym':
        return f'KEY {key_value}'
    
    return str(key_value)
