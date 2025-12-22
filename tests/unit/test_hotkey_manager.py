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
        
        # Hotkeys are now stored as KeyInfo objects
        assert manager.hotkey_record.display_name == "F1"
        assert manager.hotkey_play.display_name == "F2"
        assert manager.hotkey_stop.display_name == "ESC"
        assert manager.hotkey_spam.display_name == "F3"
    
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
        
        key_a = keyboard.KeyCode.from_char('a')
        result = manager.get_key_name(key_a)
        
        # Should return uppercase display name
        assert result == "A"


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
        with patch.object(manager, 'setup_listener'):
            manager.set_hotkey(keyboard.Key.f5, 'record')
            manager.set_hotkey(keyboard.Key.f6, 'play')
            manager.set_hotkey(keyboard.Key.esc, 'stop')
            manager.set_hotkey(keyboard.Key.f7, 'spam')
        
        # Get hotkeys (simulates saving to JSON)
        saved = manager.get_hotkeys()
        
        # Create new manager and load hotkeys (simulates loading from JSON)
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        # Verify keys are correct by display name
        assert new_manager.hotkey_record.display_name == "F5"
        assert new_manager.hotkey_play.display_name == "F6"
        assert new_manager.hotkey_stop.display_name == "ESC"
        assert new_manager.hotkey_spam.display_name == "F7"
    
    def test_save_and_load_character_keys(self):
        """Test that character keys (a, b, etc.) survive save/load roundtrip."""
        manager = HotkeyManager()
        
        # Set character keys
        key_a = keyboard.KeyCode.from_char('a')
        key_b = keyboard.KeyCode.from_char('b')
        
        with patch.object(manager, 'setup_listener'):
            manager.set_hotkey(key_a, 'record')
            manager.set_hotkey(key_b, 'play')
        
        # Get hotkeys (simulates saving to JSON)
        saved = manager.get_hotkeys()
        
        # Verify saved format is uppercase
        assert saved['record'] == 'A'
        assert saved['play'] == 'B'
        
        # Create new manager and load hotkeys
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        # Verify keys are correct
        assert new_manager.hotkey_record.display_name == 'A'
        assert new_manager.hotkey_play.display_name == 'B'
    
    def test_get_key_name_no_quotes_for_char_keys(self):
        """Test that get_key_name returns clean names without quotes."""
        manager = HotkeyManager()
        
        key_a = keyboard.KeyCode.from_char('a')
        name = manager.get_key_name(key_a)
        
        # Should be 'A' not "'A'"
        assert name == 'A'
        assert "'" not in name
        assert '"' not in name
    
    def test_hotkeys_work_after_load(self):
        """Test that loaded hotkeys are set correctly."""
        manager = HotkeyManager()
        
        # Setup with custom keys
        with patch.object(manager, 'setup_listener'):
            manager.set_hotkey(keyboard.Key.f9, 'record')
        
        saved = manager.get_hotkeys()
        
        # Load into new manager
        new_manager = HotkeyManager()
        callback_called = []
        new_manager.set_callbacks(on_record=lambda: callback_called.append('record'))
        
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        # Verify the hotkey is set correctly
        assert new_manager.hotkey_record.display_name == "F9"


class TestHotkeyManagerGetHotkeys:
    """Tests for get_hotkeys functionality."""
    
    def test_get_hotkeys_returns_display_names(self):
        """Test that get_hotkeys returns display-friendly names."""
        manager = HotkeyManager()
        
        hotkeys = manager.get_hotkeys()
        
        assert hotkeys['record'] == 'F1'
        assert hotkeys['play'] == 'F2'
        assert hotkeys['stop'] == 'ESC'
        assert hotkeys['spam'] == 'F3'
    
    def test_get_ignored_keys(self):
        """Test getting list of keys to ignore during recording."""
        manager = HotkeyManager()
        
        ignored = manager.get_ignored_keys()
        
        assert len(ignored) == 4
        assert manager.hotkey_record in ignored
        assert manager.hotkey_play in ignored
        assert manager.hotkey_stop in ignored
        assert manager.hotkey_spam in ignored

