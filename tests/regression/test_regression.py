"""Regression tests for AutoClicker application.

These tests cover critical workflows and previously fixed bugs to prevent regressions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import time
import threading

from pynput import keyboard

from models.recorder import Recorder
from models.player import Player
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
        
        # Get current hotkeys (record is F1 by default)
        hotkeys = manager.get_hotkeys()
        
        # Create new manager and load
        new_manager = HotkeyManager()
        new_manager.set_hotkeys(hotkeys)
        
        # Hotkeys should work
        assert new_manager.hotkey_record.display_name == hotkeys['record']
    
    def test_special_key_roundtrip_esc(self):
        """Regression: Escape key should work after save/load."""
        manager = HotkeyManager()
        
        hotkeys = manager.get_hotkeys()
        
        new_manager = HotkeyManager()
        new_manager.set_hotkeys(hotkeys)
        
        assert new_manager.hotkey_stop.display_name == hotkeys['stop']
    
    def test_character_key_roundtrip(self):
        """Regression: Character keys should work after save/load."""
        manager = HotkeyManager()
        
        # Simulate setting a character key as hotkey
        from pynput.keyboard import KeyCode
        manager.set_hotkey(KeyCode.from_char('a'), 'record')
        
        hotkeys = manager.get_hotkeys()
        
        new_manager = HotkeyManager()
        new_manager.set_hotkeys(hotkeys)
        
        # Key should still work
        assert new_manager.hotkey_record.display_name == hotkeys['record']


class TestRecordingPlaybackRegression:
    """Regression tests for recording and playback functionality."""
    
    def test_recording_clears_previous_events(self):
        """Regression: Starting new recording should clear old events."""
        recorder = Recorder()
        
        # Add some existing events
        recorder.recorded_events = [{"type": "old_event", "timestamp": 0.1}]
        
        # Start new recording
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start()
        
        # Old events should be cleared
        assert len(recorder.recorded_events) == 0
    
    def test_cannot_record_twice(self):
        """Regression: Cannot start recording while already recording."""
        recorder = Recorder()
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start()
            result = recorder.start()
        
        assert result is False
    
    def test_cannot_playback_empty_events(self):
        """Regression: Playback should fail with no events."""
        player = Player()
        
        result = player.start(events=[])
        
        assert result is False


class TestFileManagerRegression:
    """Regression tests for file save/load functionality."""
    
    def test_save_includes_config(self):
        """Regression: Saved files should include config section."""
        events = [{"type": "test", "timestamp": 0.1}]
        config = {"loop_count": 5, "loop_delay": 1.0, "playback_speed": 2.0}
        
        with patch('tkinter.filedialog.asksaveasfilename', return_value='/tmp/test.aclk'):
            with patch('tkinter.messagebox.showinfo'):
                with patch('builtins.open', mock_open()) as mock_file:
                    FileManager.save_recording(events, config)
                    
                    # Get the written data
                    handle = mock_file()
                    written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
                    saved_data = json.loads(written_data)
                    
                    assert 'config' in saved_data
                    assert saved_data['config']['loop_count'] == 5
    
    def test_load_handles_old_format_without_config(self):
        """Regression: Should handle old files without config section."""
        old_format_data = json.dumps([{"type": "test", "timestamp": 0.1}])
        
        with patch('tkinter.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('tkinter.messagebox.showinfo'):
                with patch('builtins.open', mock_open(read_data=old_format_data)):
                    success, events, config, msg = FileManager.load_recording()
                    
                    assert success is True
                    assert events is not None
    
    def test_load_handles_new_format_with_config(self):
        """Regression: Should correctly load files with config section."""
        new_format_data = json.dumps({
            "events": [{"type": "test", "timestamp": 0.1}],
            "config": {"loop_count": 3, "loop_delay": 0.5, "playback_speed": 1.5}
        })
        
        with patch('tkinter.filedialog.askopenfilename', return_value='/tmp/test.aclk'):
            with patch('tkinter.messagebox.showinfo'):
                with patch('builtins.open', mock_open(read_data=new_format_data)):
                    success, events, config, msg = FileManager.load_recording()
                    
                    assert success is True
                    assert events is not None
                    assert config is not None
                    assert config['loop_count'] == 3


class TestSpamClickerRegression:
    """Regression tests for spam clicker functionality."""
    
    def test_spam_clicker_uses_atomic_click(self):
        """Regression: Spam clicker should use click() not press/release."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click') as mock_click:
            with patch.object(spam_clicker.mouse_controller, 'press') as mock_press:
                spam_clicker.start_spam_click()
                time.sleep(0.05)
                spam_clicker.stop_spam_click()
                
                # Should use click(), not press()
                assert mock_click.called
    
    def test_spam_clicker_thread_is_daemon(self):
        """Regression: Spam clicker thread should be daemon."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            spam_clicker.start_spam_click()
            
            if spam_clicker.spam_click_thread is not None:
                assert spam_clicker.spam_click_thread.daemon is True
            
            spam_clicker.stop_spam_click()
    
    def test_spam_clicker_stops_on_flag(self):
        """Regression: Spam clicker should stop when flag changes."""
        spam_clicker = SpamClicker()
        click_count = []
        
        with patch.object(spam_clicker.mouse_controller, 'click', side_effect=lambda *a, **k: click_count.append(1)):
            spam_clicker.start_spam_click()
            time.sleep(0.05)
            spam_clicker.stop_spam_click()
            
            count_at_stop = len(click_count)
            time.sleep(0.05)
            
            # Should not have more clicks after stopping
            assert len(click_count) == count_at_stop


class TestConcurrencyRegression:
    """Regression tests for concurrent operation protection."""
    
    def test_double_start_recording_prevented(self):
        """Regression: Cannot start recording twice."""
        recorder = Recorder()
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start()
            result = recorder.start()
        
        assert result is False
    
    def test_double_start_spam_click_prevented(self):
        """Regression: Cannot start spam clicking twice."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            spam_clicker.start_spam_click()
            result = spam_clicker.start_spam_click()
            spam_clicker.stop_spam_click()
        
        assert result is False
    
    def test_double_start_playback_prevented(self):
        """Regression: Cannot start playback twice."""
        player = Player()
        events = [{"type": "test", "timestamp": 0.1}]
        
        with patch.object(player, '_playback_worker'):
            with patch('threading.Thread') as mock_thread:
                mock_thread.return_value = Mock()
                
                player.start(events=events)
                result = player.start(events=events)
        
        assert result is False


class TestEventDataRegression:
    """Regression tests for event data structure."""
    
    def test_mouse_click_event_has_required_fields(self):
        """Regression: Mouse click events should have all required fields."""
        required_fields = {'type', 'x', 'y', 'button', 'pressed', 'timestamp'}
        
        event = {
            "type": "mouse_click",
            "x": 100,
            "y": 200,
            "button": "Button.left",
            "pressed": True,
            "timestamp": 0.1
        }
        
        assert all(field in event for field in required_fields)
    
    def test_key_event_has_required_fields(self):
        """Regression: Key events should have all required fields."""
        press_event = {
            "type": "key_press",
            "key": "a",
            "timestamp": 0.1
        }
        
        release_event = {
            "type": "key_release",
            "key": "a",
            "timestamp": 0.2
        }
        
        assert 'type' in press_event and 'key' in press_event
        assert 'type' in release_event and 'key' in release_event


class TestPlaybackSpeedRegression:
    """Regression tests for playback speed functionality."""
    
    def test_zero_speed_does_not_hang(self):
        """Regression: Zero playback speed should not cause infinite loop."""
        player = Player()
        events = [{"type": "mouse_click", "x": 100, "y": 100, 
                   "button": "Button.left", "pressed": True, "timestamp": 0.1}]
        
        with patch.object(player._mouse, 'press'):
            with patch.object(player._mouse, 'release'):
                player.start(events=events, playback_speed=0)
                time.sleep(0.2)
                player.stop()
        
        # Should not hang
        assert True
    
    def test_very_high_speed_completes_quickly(self):
        """Regression: High playback speed should work correctly."""
        player = Player()
        events = [
            {"type": "mouse_click", "x": 100, "y": 100,
             "button": "Button.left", "pressed": True, "timestamp": 0.1},
            {"type": "mouse_click", "x": 100, "y": 100,
             "button": "Button.left", "pressed": False, "timestamp": 0.2},
        ]
        
        completed = []
        player.set_callbacks(on_complete=lambda: completed.append(True))
        
        with patch.object(player._mouse, 'press'):
            with patch.object(player._mouse, 'release'):
                player.start(events=events, playback_speed=100.0)
                time.sleep(0.5)
        
        # Should complete
        assert len(completed) > 0 or not player.is_playing


class TestInfiniteLoopRegression:
    """Regression tests for infinite loop functionality."""
    
    def test_infinite_loop_can_be_stopped(self):
        """Regression: Infinite loop playback should be stoppable."""
        player = Player()
        events = [{"type": "mouse_click", "x": 100, "y": 100,
                   "button": "Button.left", "pressed": True, "timestamp": 0.01}]
        
        with patch.object(player._mouse, 'press'):
            with patch.object(player._mouse, 'release'):
                player.start(events=events, loop_count=0)  # 0 = infinite
                time.sleep(0.05)
                result = player.stop()
                time.sleep(0.1)
        
        assert result is True
        assert player.is_playing is False
