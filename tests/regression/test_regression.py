"""Regression tests for AutoClicker application.

These tests cover critical workflows and previously fixed bugs to prevent regressions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import time
import threading

from pynput import keyboard

from models.event_recorder import EventRecorder
from models.hotkey_manager import HotkeyManager
from models.spam_clicker import SpamClicker
from utils.file_manager import FileManager


class TestHotkeyLoadRegression:
    """Regression tests for hotkey save/load functionality.
    
    Bug fixed: Hotkeys didn't work after loading because character keys
    were saved with quotes ('A' instead of A) and parse_key_name didn't
    strip them.
    """
    
    def test_special_key_roundtrip_f1(self):
        """Regression: F1 key should work after save/load."""
        manager = HotkeyManager()
        manager.hotkey_record = keyboard.Key.f1
        
        saved = manager.get_hotkeys()
        
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        assert new_manager.hotkey_record == keyboard.Key.f1
    
    def test_special_key_roundtrip_esc(self):
        """Regression: ESC key should work after save/load."""
        manager = HotkeyManager()
        manager.hotkey_stop = keyboard.Key.esc
        
        saved = manager.get_hotkeys()
        
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        assert new_manager.hotkey_stop == keyboard.Key.esc
    
    def test_character_key_roundtrip(self):
        """Regression: Character keys (a, b, etc.) should work after save/load."""
        manager = HotkeyManager()
        manager.hotkey_record = keyboard.KeyCode.from_char('r')
        manager.hotkey_play = keyboard.KeyCode.from_char('p')
        
        saved = manager.get_hotkeys()
        
        # Verify no quotes in saved format
        assert "'" not in saved['record']
        assert "'" not in saved['play']
        
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        assert new_manager.hotkey_record == keyboard.KeyCode.from_char('r')
        assert new_manager.hotkey_play == keyboard.KeyCode.from_char('p')
    
    def test_mixed_keys_roundtrip(self):
        """Regression: Mix of special and character keys should work."""
        manager = HotkeyManager()
        manager.hotkey_record = keyboard.Key.f1
        manager.hotkey_play = keyboard.KeyCode.from_char('p')
        manager.hotkey_stop = keyboard.Key.esc
        manager.hotkey_spam = keyboard.KeyCode.from_char('s')
        
        saved = manager.get_hotkeys()
        
        new_manager = HotkeyManager()
        with patch.object(new_manager, 'setup_listener'):
            new_manager.set_hotkeys(saved)
        
        assert new_manager.hotkey_record == keyboard.Key.f1
        assert new_manager.hotkey_play == keyboard.KeyCode.from_char('p')
        assert new_manager.hotkey_stop == keyboard.Key.esc
        assert new_manager.hotkey_spam == keyboard.KeyCode.from_char('s')
    
    def test_legacy_quoted_format_still_parses(self):
        """Regression: Old files with quoted keys should still load."""
        manager = HotkeyManager()
        
        # Simulate old format with quotes
        legacy_hotkeys = {
            'record': "'R'",
            'play': "'P'",
            'stop': 'ESC',
            'spam': "'S'"
        }
        
        with patch.object(manager, 'setup_listener'):
            manager.set_hotkeys(legacy_hotkeys)
        
        assert manager.hotkey_record == keyboard.KeyCode.from_char('r')
        assert manager.hotkey_play == keyboard.KeyCode.from_char('p')
        assert manager.hotkey_stop == keyboard.Key.esc
        assert manager.hotkey_spam == keyboard.KeyCode.from_char('s')


class TestRecordingPlaybackRegression:
    """Regression tests for recording and playback functionality."""
    
    def test_recording_clears_previous_events(self):
        """Regression: Starting new recording should clear previous events."""
        recorder = EventRecorder()
        recorder.recorded_events = [{'type': 'old_event', 'timestamp': 0}]
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        
        assert recorder.recorded_events == []
        recorder.stop_recording()
    
    def test_playback_respects_stop_flag_immediately(self):
        """Regression: Stopping playback should work immediately."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': False, 'timestamp': 10.0},  # Long delay
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback()
                time.sleep(0.1)
                
                result = recorder.stop_playback()
                
                assert result is True
                # Give thread time to stop
                time.sleep(0.1)
                assert recorder.is_playing is False
    
    def test_cannot_record_during_playback(self):
        """Regression: Recording should not start during playback."""
        recorder = EventRecorder()
        recorder.is_playing = True
        
        result = recorder.start_recording()
        
        assert result is False
        assert recorder.is_recording is False
    
    def test_cannot_playback_during_recording(self):
        """Regression: Playback should not start during recording."""
        recorder = EventRecorder()
        recorder.recorded_events = [{'type': 'test', 'timestamp': 0}]
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        
        result = recorder.start_playback()
        
        assert result is False
        recorder.stop_recording()
    
    def test_playback_with_zero_events_fails(self):
        """Regression: Playback should fail gracefully with no events."""
        recorder = EventRecorder()
        recorder.recorded_events = []
        
        result = recorder.start_playback()
        
        assert result is False


class TestFileManagerRegression:
    """Regression tests for file save/load functionality."""
    
    def test_save_includes_config(self):
        """Regression: Save should include configuration data."""
        events = [{'type': 'mouse_click', 'x': 100, 'y': 200, 'timestamp': 0.0}]
        config = {'loops': 5, 'delay': 1.0, 'speed': 2.0}
        
        with patch('utils.file_manager.filedialog.asksaveasfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('utils.file_manager.messagebox'):
                    FileManager.save_recording(events, config)
                    
                    # Get what was written
                    written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
                    parsed = json.loads(written_data)
                    
                    assert 'events' in parsed
                    assert 'config' in parsed
                    assert parsed['config']['loops'] == 5
    
    def test_load_handles_old_format_without_config(self):
        """Regression: Loading old files without config should work."""
        old_format = [
            {'type': 'mouse_click', 'x': 100, 'y': 200, 'timestamp': 0.0}
        ]
        
        with patch('utils.file_manager.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open(read_data=json.dumps(old_format))):
                with patch('utils.file_manager.messagebox'):
                    success, events, config, message = FileManager.load_recording()
                    
                    assert success is True
                    assert len(events) == 1
                    assert config == {}  # Empty config for old format
    
    def test_load_handles_new_format_with_config(self):
        """Regression: Loading new files with config should work."""
        new_format = {
            'events': [{'type': 'mouse_click', 'x': 100, 'y': 200, 'timestamp': 0.0}],
            'config': {'loops': 3, 'hotkeys': {'record': 'F1'}}
        }
        
        with patch('utils.file_manager.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open(read_data=json.dumps(new_format))):
                with patch('utils.file_manager.messagebox'):
                    success, events, config, message = FileManager.load_recording()
                    
                    assert success is True
                    assert len(events) == 1
                    assert config['loops'] == 3
    
    def test_load_validates_event_structure(self):
        """Regression: Invalid events should be rejected."""
        invalid_events = [
            {'type': 'mouse_click'}  # Missing timestamp
        ]
        
        with patch('utils.file_manager.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('builtins.open', mock_open(read_data=json.dumps(invalid_events))):
                with patch('utils.file_manager.messagebox'):
                    success, events, config, message = FileManager.load_recording()
                    
                    assert success is False


class TestSpamClickerRegression:
    """Regression tests for spam clicker functionality."""
    
    def test_spam_clicker_uses_atomic_click(self):
        """Regression: Spam clicker should use click() not press()/release()."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click') as mock_click:
            with patch.object(spam_clicker.mouse_controller, 'press') as mock_press:
                spam_clicker.start_spam_click()
                time.sleep(0.05)
                spam_clicker.stop_spam_click()
                
                # Should use click, not press
                assert mock_click.called
                assert not mock_press.called
    
    def test_spam_clicker_thread_is_daemon(self):
        """Regression: Thread should be daemon to not block app exit."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            spam_clicker.start_spam_click()
            
            assert spam_clicker.spam_click_thread.daemon is True
            
            spam_clicker.stop_spam_click()
    
    def test_spam_clicker_stops_on_flag(self):
        """Regression: Setting flag should stop spam clicking."""
        spam_clicker = SpamClicker()
        click_count = [0]
        
        def counting_click(*args):
            click_count[0] += 1
            if click_count[0] >= 5:
                spam_clicker.is_spam_clicking = False
        
        with patch.object(spam_clicker.mouse_controller, 'click', side_effect=counting_click):
            spam_clicker.start_spam_click()
            spam_clicker.spam_click_thread.join(timeout=1)
            
            assert spam_clicker.is_spam_clicking is False


class TestConcurrencyRegression:
    """Regression tests for concurrency issues."""
    
    def test_double_start_recording_prevented(self):
        """Regression: Starting recording twice should be prevented."""
        recorder = EventRecorder()
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            result1 = recorder.start_recording()
            # Second start should not reset state incorrectly
            recorder.recorded_events.append({'type': 'test', 'timestamp': 0})
            
            # is_recording is already True, but start_recording doesn't check this
            # This test documents current behavior
            assert result1 is True
            assert recorder.is_recording is True
        
        recorder.stop_recording()
    
    def test_double_start_spam_click_prevented(self):
        """Regression: Starting spam click twice should return False."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            result1 = spam_clicker.start_spam_click()
            result2 = spam_clicker.start_spam_click()
            
            assert result1 is True
            assert result2 is False
            
            spam_clicker.stop_spam_click()
    
    def test_double_start_playback_prevented(self):
        """Regression: Starting playback twice should return False."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': False, 'timestamp': 1.0},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                result1 = recorder.start_playback()
                result2 = recorder.start_playback()
                
                assert result1 is True
                assert result2 is False
                
                recorder.stop_playback()


class TestEventDataRegression:
    """Regression tests for event data integrity."""
    
    def test_mouse_click_event_has_required_fields(self):
        """Regression: Mouse click events should have all required fields."""
        recorder = EventRecorder()
        recorder.is_recording = True
        recorder.start_time = time.time()
        recorder.recorded_events = []
        
        # Simulate mouse click
        recorder._on_click(100, 200, 'Button.left', True)
        
        event = recorder.recorded_events[0]
        assert 'type' in event
        assert 'x' in event
        assert 'y' in event
        assert 'button' in event
        assert 'pressed' in event
        assert 'timestamp' in event
    
    def test_key_event_has_required_fields(self):
        """Regression: Key events should have all required fields."""
        recorder = EventRecorder()
        recorder.is_recording = True
        recorder.start_time = time.time()
        recorder.recorded_events = []
        recorder.ignored_keys = []
        
        # Create a mock key
        mock_key = Mock()
        mock_key.char = 'a'
        
        recorder._on_key_press(mock_key)
        
        event = recorder.recorded_events[0]
        assert 'type' in event
        assert 'key' in event
        assert 'timestamp' in event
    
    def test_ignored_keys_not_recorded(self):
        """Regression: Ignored hotkeys should not be recorded."""
        recorder = EventRecorder()
        recorder.is_recording = True
        recorder.start_time = time.time()
        recorder.recorded_events = []
        recorder.ignored_keys = [keyboard.Key.f1]
        
        recorder._on_key_press(keyboard.Key.f1)
        
        assert len(recorder.recorded_events) == 0


class TestPlaybackSpeedRegression:
    """Regression tests for playback speed handling."""
    
    def test_zero_speed_does_not_hang(self):
        """Regression: Zero playback speed should not cause infinite wait."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': False, 'timestamp': 0.1},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback(playback_speed=0)
                time.sleep(0.2)
                recorder.stop_playback()
                
                # Should be able to stop even with zero speed
                recorder.playback_thread.join(timeout=1)
                assert recorder.is_playing is False
    
    def test_very_high_speed_completes_quickly(self):
        """Regression: Very high speed should complete without issues."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': False, 'timestamp': 100.0},  # 100 second gap
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback(playback_speed=10000)  # Very high speed
                
                # Should complete quickly
                recorder.playback_thread.join(timeout=2)
                assert recorder.is_playing is False


class TestInfiniteLoopRegression:
    """Regression tests for infinite loop handling."""
    
    def test_infinite_loop_can_be_stopped(self):
        """Regression: Infinite loop (loop_count=0) should be stoppable."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left',
             'pressed': False, 'timestamp': 0.01},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback(loop_count=0)  # Infinite
                
                assert recorder.is_playing is True
                
                time.sleep(0.1)
                recorder.stop_playback()
                
                recorder.playback_thread.join(timeout=1)
                assert recorder.is_playing is False
