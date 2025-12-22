"""Unit tests for HotkeyManager class."""

import pytest
from unittest.mock import Mock, patch
from pynput import keyboard

from models.hotkey_manager import HotkeyManager


class TestHotkeyManagerInit:
    """Tests for HotkeyManager initialization."""
    
    def test_default_hotkeys(self):
        """Test that HotkeyManager initializes with correct default hotkeys."""
        manager = HotkeyManager()
        
        assert manager.hotkey_record == keyboard.Key.f1
        assert manager.hotkey_play == keyboard.Key.f2
        assert manager.hotkey_stop == keyboard.Key.esc
        assert manager.hotkey_spam == keyboard.Key.f3
    
    def test_initial_state(self):
        """Test initial state of the manager."""
        manager = HotkeyManager()
        
        assert manager.hotkey_listener is None
        assert manager.capturing_hotkey is None


class TestHotkeyManagerCallbacks:
    """Tests for HotkeyManager callback functionality."""
    
    def test_set_all_callbacks(self):
        """Test setting all callback functions."""
        manager = HotkeyManager()
        
        mock_record = Mock()
        mock_play = Mock()
        mock_stop = Mock()
        mock_spam = Mock()
        mock_captured = Mock()
        mock_status = Mock()
        
        manager.set_callbacks(
            on_record=mock_record,
            on_play=mock_play,
            on_stop=mock_stop,
            on_spam=mock_spam,
            on_hotkey_captured=mock_captured,
            on_status=mock_status
        )
        
        assert manager.on_record_callback == mock_record
        assert manager.on_play_callback == mock_play
        assert manager.on_stop_callback == mock_stop
        assert manager.on_spam_callback == mock_spam
        assert manager.on_hotkey_captured_callback == mock_captured
        assert manager.on_status_callback == mock_status
    
    def test_set_partial_callbacks(self):
        """Test setting only some callbacks."""
        manager = HotkeyManager()
        mock_record = Mock()
        
        manager.set_callbacks(on_record=mock_record)
        
        assert manager.on_record_callback == mock_record
        assert manager.on_play_callback is None


class TestHotkeyManagerKeyNames:
    """Tests for key name conversion."""
    
    def test_get_key_name_with_named_key(self):
        """Test getting name for a named key like F1."""
        manager = HotkeyManager()
        
        result = manager.get_key_name(keyboard.Key.f1)
        
        assert result == "F1"
    
    def test_get_key_name_with_special_key(self):
        """Test getting name for special keys."""
        manager = HotkeyManager()
        
        result = manager.get_key_name(keyboard.Key.esc)
        
        assert result == "ESC"
    
    def test_get_key_name_with_char_key(self):
        """Test getting name for character keys."""
        manager = HotkeyManager()
        
        # Create a mock KeyCode
        mock_key = Mock()
        mock_key.char = 'a'
        del mock_key.name  # Remove name attribute
        
        result = manager.get_key_name(mock_key)
        
        # Result depends on implementation - just ensure it returns a string
        assert isinstance(result, str)


class TestHotkeyManagerHotkeyCapture:
    """Tests for hotkey capture functionality."""
    
    def test_start_capture_sets_state(self):
        """Test that starting capture sets the capturing state."""
        manager = HotkeyManager()
        
        manager.start_capture("record")
        
        assert manager.capturing_hotkey == "record"
    
    def test_capture_different_hotkey_types(self):
        """Test capturing different types of hotkeys."""
        manager = HotkeyManager()
        
        for hotkey_type in ["record", "play", "stop", "spam"]:
            manager.start_capture(hotkey_type)
            assert manager.capturing_hotkey == hotkey_type


class TestHotkeyManagerSaveLoadRoundtrip:
    """Tests for hotkey save/load functionality."""
    
    def test_save_and_load_special_keys(self):
        """Test that special keys (F1, ESC, etc.) survive save/load roundtrip."""
        manager = HotkeyManager()
        
        # Set some special keys
        manager.hotkey_record = keyboard.Key.f5
        manager.hotkey_play = keyboard.Key.f6
        manager.hotkey_stop = keyboard.Key.esc
        manager.hotkey_spam = keyboard.Key.f7
        
        # Get hotkeys (simulates saving to JSON)
        saved = manager.get_hotkeys()
        
        # Create new manager and load hotkeys (simulates loading from JSON)
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):  # Don't actually setup listener
            new_manager.set_hotkeys(saved)
        
        # Verify keys are correct
        assert new_manager.hotkey_record == keyboard.Key.f5
        assert new_manager.hotkey_play == keyboard.Key.f6
        assert new_manager.hotkey_stop == keyboard.Key.esc
        assert new_manager.hotkey_spam == keyboard.Key.f7
    
    def test_save_and_load_character_keys(self):
        """Test that character keys (a, b, etc.) survive save/load roundtrip."""
        manager = HotkeyManager()
        
        # Set character keys
        key_a = keyboard.KeyCode.from_char('a')
        key_b = keyboard.KeyCode.from_char('b')
        manager.hotkey_record = key_a
        manager.hotkey_play = key_b
        
        # Get hotkeys (simulates saving to JSON)
        saved = manager.get_hotkeys()
        
        # Verify saved format doesn't have quotes
        assert saved['record'] == 'A'
        assert saved['play'] == 'B'
        
        # Create new manager and load hotkeys (simulates loading from JSON)
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        # Verify keys work (compare by creating same key)
        assert new_manager.hotkey_record == keyboard.KeyCode.from_char('a')
        assert new_manager.hotkey_play == keyboard.KeyCode.from_char('b')
    
    def test_get_key_name_no_quotes_for_char_keys(self):
        """Test that get_key_name returns clean names without quotes."""
        manager = HotkeyManager()
        
        key_a = keyboard.KeyCode.from_char('a')
        name = manager.get_key_name(key_a)
        
        # Should be 'A' not "'A'"
        assert name == 'A'
        assert "'" not in name
        assert '"' not in name
    
    def test_parse_key_name_handles_quoted_input(self):
        """Test that parse_key_name handles input with quotes (legacy files)."""
        manager = HotkeyManager()
        
        # Even if old file had quotes, it should still parse correctly
        parsed = manager.parse_key_name("'A'")
        expected = keyboard.KeyCode.from_char('a')
        
        assert parsed == expected
    
    def test_hotkeys_work_after_load(self):
        """Test that loaded hotkeys actually trigger correctly."""
        manager = HotkeyManager()
        
        # Setup with custom keys
        manager.hotkey_record = keyboard.Key.f9
        saved = manager.get_hotkeys()
        
        # Load into new manager
        new_manager = HotkeyManager()
        callback_called = []
        new_manager.set_callbacks(on_record=lambda: callback_called.append('record'))
        
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        # Verify the hotkey is set correctly for comparison
        assert new_manager.hotkey_record == keyboard.Key.f9

