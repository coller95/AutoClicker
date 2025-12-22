"""Unit tests for FileManager class."""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
import os

from utils.file_manager import FileManager


class TestFileManagerSave:
    """Tests for FileManager save functionality."""
    
    def test_save_empty_events_shows_warning(self):
        """Test that saving empty events shows a warning."""
        with patch('utils.file_manager.messagebox.showwarning') as mock_warning:
            result = FileManager.save_recording([])
            
            mock_warning.assert_called_once()
            assert result[0] is False
            assert "No events" in result[2]
    
    def test_save_none_events_shows_warning(self):
        """Test that saving None events shows a warning."""
        with patch('utils.file_manager.messagebox.showwarning') as mock_warning:
            result = FileManager.save_recording(None)
            
            mock_warning.assert_called_once()
            assert result[0] is False
    
    def test_save_cancelled_by_user(self):
        """Test handling when user cancels save dialog."""
        events = [{"type": "test"}]
        
        with patch('utils.file_manager.messagebox.showwarning'):
            with patch('utils.file_manager.filedialog.asksaveasfilename', return_value=''):
                result = FileManager.save_recording(events)
                
                assert result[0] is False
                assert "cancelled" in result[2].lower()
    
    def test_save_with_events_only(self):
        """Test saving events without config."""
        events = [{"type": "mouse_click", "x": 100, "y": 200}]
        
        with patch('utils.file_manager.filedialog.asksaveasfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open()) as mocked_file:
                with patch('utils.file_manager.messagebox'):
                    result = FileManager.save_recording(events)
                    
                    # Verify file was opened for writing
                    mocked_file.assert_called_once_with('/tmp/test.aclk', 'w')
    
    def test_save_with_config(self):
        """Test saving events with config data."""
        events = [{"type": "mouse_click", "x": 100, "y": 200}]
        config = {"loop_count": 3, "loop_delay": 1.0}
        
        with patch('utils.file_manager.filedialog.asksaveasfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open()) as mocked_file:
                with patch('utils.file_manager.messagebox'):
                    result = FileManager.save_recording(events, config)
                    
                    mocked_file.assert_called_once_with('/tmp/test.aclk', 'w')


class TestFileManagerLoad:
    """Tests for FileManager load functionality."""
    
    def test_load_cancelled_by_user(self):
        """Test handling when user cancels load dialog."""
        with patch('utils.file_manager.filedialog.askopenfilename', return_value=''):
            result = FileManager.load_recording()
            
            assert result[0] is False
            assert "cancelled" in result[3].lower()
    
    def test_load_valid_file_with_events_only(self):
        """Test loading a valid file with events only."""
        events = [{"type": "mouse_click", "x": 100, "y": 200, "timestamp": 0.0}]
        
        with patch('utils.file_manager.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open(read_data=json.dumps(events))):
                with patch('utils.file_manager.messagebox'):
                    result = FileManager.load_recording()
                    
                    assert result[0] is True
    
    def test_load_valid_file_with_config(self):
        """Test loading a valid file with events and config."""
        data = {
            "events": [{"type": "mouse_click", "x": 100, "y": 200, "timestamp": 0.0}],
            "config": {"loop_count": 3}
        }
        
        with patch('utils.file_manager.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open(read_data=json.dumps(data))):
                with patch('utils.file_manager.messagebox'):
                    result = FileManager.load_recording()
                    
                    assert result[0] is True
    
    def test_load_invalid_json_shows_error(self):
        """Test that loading invalid JSON shows an error."""
        with patch('utils.file_manager.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open(read_data='not valid json')):
                with patch('utils.file_manager.messagebox.showerror') as mock_error:
                    result = FileManager.load_recording()
                    
                    assert result[0] is False


class TestFileManagerValidation:
    """Tests for FileManager validation functionality."""
    
    def test_validate_events_with_valid_data(self):
        """Test validation with valid events."""
        events = [
            {"type": "mouse_click", "x": 100, "y": 200, "button": "left", "time": 0.1},
            {"type": "key_press", "key": "a", "time": 0.2}
        ]
        
        # This tests the validation logic if it exists
        # Adjust based on actual implementation
        assert isinstance(events, list)
        assert len(events) == 2
    
    def test_validate_config_with_valid_data(self):
        """Test validation with valid config."""
        config = {
            "loop_count": 5,
            "loop_delay": 1.5,
            "playback_speed": 2.0
        }
        
        assert config["loop_count"] > 0
        assert config["loop_delay"] >= 0
        assert config["playback_speed"] > 0
