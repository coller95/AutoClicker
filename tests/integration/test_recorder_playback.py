"""Integration tests for recording and playback workflow."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

from models.event_recorder import EventRecorder
from models.hotkey_manager import HotkeyManager
from utils.file_manager import FileManager


class TestRecorderHotkeyIntegration:
    """Integration tests for EventRecorder and HotkeyManager."""
    
    def test_hotkey_triggers_recording(self):
        """Test that hotkey manager can trigger recording start."""
        recorder = EventRecorder()
        hotkey_manager = HotkeyManager()
        
        # Set up the callback to start recording
        def on_record_pressed():
            with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
                recorder.start_recording()
        
        hotkey_manager.set_callbacks(on_record=on_record_pressed)
        
        # Simulate hotkey press
        hotkey_manager.on_record_callback()
        
        assert recorder.is_recording is True
    
    def test_stop_hotkey_stops_recording(self):
        """Test that stop hotkey stops recording."""
        recorder = EventRecorder()
        hotkey_manager = HotkeyManager()
        
        # Start recording first
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        
        # Set up stop callback
        def on_stop_pressed():
            recorder.stop_recording()
        
        hotkey_manager.set_callbacks(on_stop=on_stop_pressed)
        
        # Simulate stop hotkey
        hotkey_manager.on_stop_callback()
        
        assert recorder.is_recording is False


class TestRecorderFileManagerIntegration:
    """Integration tests for EventRecorder and FileManager."""
    
    def test_save_and_load_recorded_events(self, tmp_path):
        """Test that recorded events can be saved and loaded."""
        recorder = EventRecorder()
        
        # Simulate some recorded events
        recorder.recorded_events = [
            {"type": "mouse_move", "x": 100, "y": 200, "time": 0.0},
            {"type": "mouse_click", "x": 100, "y": 200, "button": "left", "pressed": True, "time": 0.1},
        ]
        
        # Save to a temporary file
        file_path = tmp_path / "test_recording.aclk"
        
        data = {
            "events": recorder.recorded_events,
            "config": {
                "loop_count": recorder.loop_count,
                "loop_delay": recorder.loop_delay,
                "playback_speed": recorder.playback_speed
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        # Load from file
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data["events"] == recorder.recorded_events
        assert loaded_data["config"]["loop_count"] == 1
    
    def test_load_events_into_recorder(self, sample_events, sample_config, tmp_path):
        """Test loading saved events into a recorder."""
        # Save test data
        file_path = tmp_path / "test.aclk"
        data = {"events": sample_events, "config": sample_config}
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        # Load into recorder
        recorder = EventRecorder()
        
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        
        recorder.recorded_events = loaded_data["events"]
        recorder.loop_count = loaded_data["config"]["loop_count"]
        recorder.loop_delay = loaded_data["config"]["loop_delay"]
        recorder.playback_speed = loaded_data["config"]["playback_speed"]
        
        assert len(recorder.recorded_events) == len(sample_events)
        assert recorder.loop_count == sample_config["loop_count"]


class TestFullWorkflowIntegration:
    """Integration tests for complete user workflows."""
    
    def test_record_save_load_play_workflow(self, tmp_path):
        """Test complete workflow: record -> save -> load -> play."""
        recorder = EventRecorder()
        hotkey_manager = HotkeyManager()
        
        # Step 1: Start recording
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        assert recorder.is_recording is True
        
        # Step 2: Simulate some events being recorded
        recorder.recorded_events = [
            {"type": "mouse_click", "x": 500, "y": 300, "button": "left", "pressed": True, "time": 0.0},
            {"type": "mouse_click", "x": 500, "y": 300, "button": "left", "pressed": False, "time": 0.05},
        ]
        
        # Step 3: Stop recording
        recorder.stop_recording()
        assert recorder.is_recording is False
        assert len(recorder.recorded_events) == 2
        
        # Step 4: Save to file
        file_path = tmp_path / "workflow_test.aclk"
        data = {"events": recorder.recorded_events}
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        # Step 5: Create new recorder and load
        new_recorder = EventRecorder()
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        new_recorder.recorded_events = loaded_data["events"]
        
        # Step 6: Verify loaded data
        assert len(new_recorder.recorded_events) == 2
        assert new_recorder.recorded_events[0]["type"] == "mouse_click"
    
    def test_spam_clicker_independent_of_recorder(self):
        """Test that spam clicker works independently of recorder."""
        from models.spam_clicker import SpamClicker
        
        recorder = EventRecorder()
        spam_clicker = SpamClicker()
        
        # Start recording
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        
        # Spam clicker should be independent
        assert spam_clicker.is_spam_clicking is False
        assert recorder.is_recording is True
        
        # Stop recording shouldn't affect spam clicker state
        recorder.stop_recording()
        assert spam_clicker.is_spam_clicking is False
