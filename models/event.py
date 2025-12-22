"""Event data models for recording and playback."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class EventType(Enum):
    """Types of recordable events."""
    MOUSE_CLICK = "mouse_click"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"


@dataclass
class MouseEvent:
    """Represents a mouse click event."""
    x: int
    y: int
    button: str
    pressed: bool
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'type': EventType.MOUSE_CLICK.value,
            'x': self.x,
            'y': self.y,
            'button': self.button,
            'pressed': self.pressed,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseEvent':
        """Create from dictionary."""
        return cls(
            x=data['x'],
            y=data['y'],
            button=data['button'],
            pressed=data['pressed'],
            timestamp=data['timestamp']
        )


@dataclass
class KeyEvent:
    """Represents a keyboard event."""
    key: str
    pressed: bool  # True for press, False for release
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        event_type = EventType.KEY_PRESS.value if self.pressed else EventType.KEY_RELEASE.value
        return {
            'type': event_type,
            'key': self.key,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyEvent':
        """Create from dictionary."""
        pressed = data['type'] == EventType.KEY_PRESS.value
        return cls(
            key=data['key'],
            pressed=pressed,
            timestamp=data['timestamp']
        )


@dataclass
class RecordingSession:
    """Container for a recording session with events and metadata."""
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_event(self, event: Dict[str, Any]):
        """Add an event to the recording."""
        self.events.append(event)
    
    def clear(self):
        """Clear all recorded events."""
        self.events.clear()
    
    def __len__(self):
        return len(self.events)
    
    def __iter__(self):
        return iter(self.events)


@dataclass 
class PlaybackConfig:
    """Configuration for event playback."""
    loop_count: int = 1      # 0 = infinite
    loop_delay: float = 0.0  # seconds between loops
    playback_speed: float = 1.0  # multiplier
    
    @property
    def is_infinite(self) -> bool:
        """Check if playback should loop infinitely."""
        return self.loop_count == 0
