"""Unit tests for Recorder and Player classes."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from models.recorder import Recorder
from models.player import Player


class TestRecorderInit:
    """Tests for Recorder initialization."""
    
    def test_initial_state(self):
        """Test that Recorder initializes with correct default state."""
        recorder = Recorder()
        
        assert recorder.is_recording is False
        assert recorder.recorded_events == []
        assert recorder.start_time is None
    
    def test_event_count(self):
        """Test that event count property works."""
        recorder = Recorder()
        
        assert recorder.event_count == 0
        recorder.recorded_events = [{"type": "test"}, {"type": "test2"}]
        assert recorder.event_count == 2


class TestPlayerInit:
    """Tests for Player initialization."""
    
    def test_initial_state(self):
        """Test that Player initializes with correct default state."""
        player = Player()
        
        assert player.is_playing is False


class TestRecorderCallbacks:
    """Tests for Recorder callback functionality."""
    
    def test_set_callbacks(self):
        """Test setting callback functions."""
        recorder = Recorder()
        
        mock_on_event = Mock()
        mock_on_status = Mock()
        mock_on_live_input = Mock()
        
        recorder.set_callbacks(
            on_event=mock_on_event,
            on_status=mock_on_status,
            on_live_input=mock_on_live_input
        )
        
        assert recorder._on_event == mock_on_event
        assert recorder._on_status == mock_on_status
        assert recorder._on_live_input == mock_on_live_input
    
    def test_set_partial_callbacks(self):
        """Test setting only some callbacks."""
        recorder = Recorder()
        mock_on_event = Mock()
        
        recorder.set_callbacks(on_event=mock_on_event)
        
        assert recorder._on_event == mock_on_event
        assert recorder._on_status is None


class TestPlayerCallbacks:
    """Tests for Player callback functionality."""
    
    def test_set_callbacks(self):
        """Test setting callback functions."""
        player = Player()
        
        mock_on_status = Mock()
        mock_on_complete = Mock()
        
        player.set_callbacks(
            on_status=mock_on_status,
            on_complete=mock_on_complete
        )
        
        assert player._on_status == mock_on_status
        assert player._on_complete == mock_on_complete


class TestRecorderRecording:
    """Tests for Recorder recording functionality."""
    
    def test_start_recording_changes_state(self):
        """Test that starting recording changes the recording state."""
        recorder = Recorder()
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start()
        
        assert recorder.is_recording is True
        assert recorder.recorded_events == []
    
    def test_cannot_start_while_recording(self):
        """Test that recording cannot start twice."""
        recorder = Recorder()
        recorder.is_recording = True
        
        result = recorder.start()
        
        assert result is False


class TestPlayerPlayback:
    """Tests for Player playback functionality."""
    
    def test_cannot_play_empty_recording(self):
        """Test that playback fails with no recorded events."""
        player = Player()
        
        result = player.start(events=[])
        
        assert result is False
    
    def test_cannot_play_while_playing(self):
        """Test that playback cannot start during playback."""
        player = Player()
        player.is_playing = True
        
        result = player.start(events=[{"type": "test"}])
        
        assert result is False
    
    def test_playback_settings_passed(self):
        """Test setting playback parameters."""
        player = Player()
        
        events = [{"type": "test", "timestamp": 0.1}]
        
        with patch.object(player, '_playback_worker'):
            # Mock the thread to prevent actual playback
            with patch('threading.Thread') as mock_thread:
                mock_thread_instance = Mock()
                mock_thread.return_value = mock_thread_instance
                
                result = player.start(
                    events=events,
                    loop_count=5,
                    loop_delay=2.0,
                    playback_speed=0.5
                )
                
                assert result is True
                assert player.is_playing is True
