"""Unit tests for EventRecorder class."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from models.event_recorder import EventRecorder


class TestEventRecorderInit:
    """Tests for EventRecorder initialization."""
    
    def test_initial_state(self):
        """Test that EventRecorder initializes with correct default state."""
        recorder = EventRecorder()
        
        assert recorder.is_recording is False
        assert recorder.is_playing is False
        assert recorder.recorded_events == []
        assert recorder.start_time is None
        assert recorder.loop_count == 1
        assert recorder.loop_delay == 0.0
        assert recorder.playback_speed == 1.0
    
    def test_controllers_initialized(self):
        """Test that mouse and keyboard controllers are initialized."""
        recorder = EventRecorder()
        
        assert recorder.mouse_controller is not None
        assert recorder.keyboard_controller is not None


class TestEventRecorderCallbacks:
    """Tests for EventRecorder callback functionality."""
    
    def test_set_callbacks(self):
        """Test setting callback functions."""
        recorder = EventRecorder()
        
        mock_on_event = Mock()
        mock_on_status = Mock()
        mock_on_complete = Mock()
        
        recorder.set_callbacks(
            on_event=mock_on_event,
            on_status=mock_on_status,
            on_playback_complete=mock_on_complete
        )
        
        assert recorder.on_event_callback == mock_on_event
        assert recorder.on_status_callback == mock_on_status
        assert recorder.on_playback_complete_callback == mock_on_complete
    
    def test_set_partial_callbacks(self):
        """Test setting only some callbacks."""
        recorder = EventRecorder()
        mock_on_event = Mock()
        
        recorder.set_callbacks(on_event=mock_on_event)
        
        assert recorder.on_event_callback == mock_on_event
        assert recorder.on_status_callback is None


class TestEventRecorderRecording:
    """Tests for EventRecorder recording functionality."""
    
    def test_start_recording_changes_state(self):
        """Test that starting recording changes the recording state."""
        recorder = EventRecorder()
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        
        assert recorder.is_recording is True
        assert recorder.recorded_events == []
    
    def test_cannot_record_while_playing(self):
        """Test that recording cannot start during playback."""
        recorder = EventRecorder()
        recorder.is_playing = True
        
        result = recorder.start_recording()
        
        assert result is False
        assert recorder.is_recording is False


class TestEventRecorderPlayback:
    """Tests for EventRecorder playback functionality."""
    
    def test_playback_settings(self):
        """Test setting playback parameters."""
        recorder = EventRecorder()
        
        recorder.loop_count = 5
        recorder.loop_delay = 2.0
        recorder.playback_speed = 0.5
        
        assert recorder.loop_count == 5
        assert recorder.loop_delay == 2.0
        assert recorder.playback_speed == 0.5
    
    def test_cannot_play_empty_recording(self):
        """Test that playback fails with no recorded events."""
        recorder = EventRecorder()
        recorder.recorded_events = []
        
        result = recorder.start_playback()
        
        assert result is False
    
    def test_cannot_play_while_recording(self):
        """Test that playback cannot start during recording."""
        recorder = EventRecorder()
        recorder.is_recording = True
        recorder.recorded_events = [{"type": "test"}]
        
        result = recorder.start_playback()
        
        assert result is False
