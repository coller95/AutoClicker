"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_events():
    """Sample recorded events for testing."""
    return [
        {"type": "mouse_move", "x": 100, "y": 200, "time": 0.0},
        {"type": "mouse_click", "x": 100, "y": 200, "button": "left", "pressed": True, "time": 0.1},
        {"type": "mouse_click", "x": 100, "y": 200, "button": "left", "pressed": False, "time": 0.15},
        {"type": "key_press", "key": "a", "time": 0.5},
        {"type": "key_release", "key": "a", "time": 0.55},
    ]


@pytest.fixture
def sample_config():
    """Sample configuration data for testing."""
    return {
        "loop_count": 3,
        "loop_delay": 1.0,
        "playback_speed": 1.0,
    }


@pytest.fixture
def temp_recording_file(tmp_path, sample_events, sample_config):
    """Create a temporary recording file for testing."""
    import json
    
    file_path = tmp_path / "test_recording.aclk"
    data = {
        "events": sample_events,
        "config": sample_config
    }
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return file_path
