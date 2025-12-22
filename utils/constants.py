"""Application constants - colors, fonts, and default values."""

# =============================================================================
# COLORS
# =============================================================================

class Colors:
    """Color constants for the application."""
    
    # Button colors
    RECORD = "#4CAF50"       # Green
    RECORD_ACTIVE = "#f44336"  # Red
    PLAY = "#2196F3"         # Blue
    PLAY_ACTIVE = "#f44336"  # Red
    CLEAR = "#FF9800"        # Orange
    SAVE = "#9C27B0"         # Purple
    LOAD = "#009688"         # Teal
    
    # Status colors
    STATUS_OK = "green"
    STATUS_ERROR = "red"
    STATUS_INFO = "blue"
    STATUS_DEFAULT = "black"
    
    # Banner colors
    BANNER_RECORDING = "#f44336"   # Red
    BANNER_PLAYING = "#2196F3"     # Blue
    BANNER_SPAM = "#FF9800"        # Orange
    BANNER_WARNING = "#d32f2f"     # Dark red
    
    # Live input display
    INPUT_HIGHLIGHT = "#FFEB3B"    # Yellow
    COUNTDOWN_HIGHLIGHT = "#4FC3F7"  # Light blue
    
    # UI elements
    BUTTON_TEXT = "white"
    HOTKEY_CAPTURE = "yellow"
    HOTKEY_DEFAULT = "gray85"
    INFO_TEXT = "gray"


# =============================================================================
# FONTS
# =============================================================================

class Fonts:
    """Font constants for the application."""
    
    TITLE = ("Arial", 12, "bold")
    BUTTON = ("Arial", 9, "bold")
    LABEL = ("Arial", 8)
    LABEL_SMALL = ("Arial", 7)
    STATUS = ("Arial", 9)
    EVENT_LOG = ("Courier", 8)
    BANNER_MAIN = ("Arial", 12, "bold")
    BANNER_STATUS = ("Arial", 9)
    BANNER_INPUT = ("Arial", 10)
    BANNER_COUNTDOWN = ("Arial", 11, "bold")
    HOTKEY_BUTTON = ("Arial", 8)
    INFO = ("Arial", 7)


# =============================================================================
# WINDOW SETTINGS
# =============================================================================

class Window:
    """Window configuration constants."""
    
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 500
    MIN_WIDTH = 750
    MIN_HEIGHT = 450
    LEFT_PANEL_WIDTH = 280


# =============================================================================
# DEFAULT VALUES
# =============================================================================

class Defaults:
    """Default values for settings."""
    
    # Loop settings
    LOOP_COUNT = 0          # 0 = infinite
    LOOP_DELAY = 0.0        # seconds
    PLAYBACK_SPEED = 1.0    # multiplier
    
    # Spam clicker
    SPAM_CLICK_DELAY = 0.01  # 10ms = 100 clicks/second
    
    # Spinbox ranges
    LOOP_MIN = 0
    LOOP_MAX = 100
    DELAY_MIN = 0
    DELAY_MAX = 60
    DELAY_INCREMENT = 0.5
    SPEED_MIN = 0.1
    SPEED_MAX = 10.0
    SPEED_INCREMENT = 0.1


# =============================================================================
# BORDER SETTINGS
# =============================================================================

class Border:
    """Border overlay settings."""
    
    THICKNESS = 4
    BANNER_PADDING_X = 12
    BANNER_PADDING_Y = 8
    BANNER_OFFSET = 10  # Offset from monitor edge
