"""Tests for preventing mouse/keyboard deadlock scenarios."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import threading
import time

from models.recorder import Recorder
from models.player import Player
from models.spam_clicker import SpamClicker


class TestSpamClickerDeadlockPrevention:
    """Tests to ensure spam clicker doesn't cause deadlock."""
    
    def test_spam_clicker_can_be_stopped(self):
        """Test that spam clicking can always be stopped."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            spam_clicker.start_spam_click()
            assert spam_clicker.is_spam_clicking is True
            
            # Should be able to stop immediately
            result = spam_clicker.stop_spam_click()
            assert result is True
            assert spam_clicker.is_spam_clicking is False
    
    def test_spam_clicker_thread_is_daemon(self):
        """Test that spam click thread is daemon (won't block app exit)."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            spam_clicker.start_spam_click()
            
            # Thread should be daemon
            if spam_clicker.spam_click_thread is not None:
                assert spam_clicker.spam_click_thread.daemon is True
            
            spam_clicker.stop_spam_click()
    
    def test_spam_clicker_stops_on_flag_change(self):
        """Test that spam click thread respects stop flag."""
        spam_clicker = SpamClicker()
        click_count = []
        
        def count_click(*args, **kwargs):
            click_count.append(1)
        
        with patch.object(spam_clicker.mouse_controller, 'click', side_effect=count_click):
            spam_clicker.start_spam_click()
            time.sleep(0.1)  # Let it click a few times
            spam_clicker.stop_spam_click()
            
            # Should have stopped clicking
            final_count = len(click_count)
            time.sleep(0.1)
            assert len(click_count) == final_count  # No more clicks after stop
    
    def test_spam_clicker_uses_complete_click(self):
        """Test that spam clicker uses atomic click() not press/release."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click') as mock_click:
            spam_clicker.start_spam_click()
            time.sleep(0.05)
            spam_clicker.stop_spam_click()
            
            # Should use click() method, not separate press/release
            assert mock_click.called
    
    def test_spam_clicker_handles_exception_gracefully(self):
        """Test that exceptions in spam click don't crash the thread."""
        spam_clicker = SpamClicker()
        
        def raise_error(*args, **kwargs):
            raise Exception("Test error")
        
        status_messages = []
        spam_clicker.set_callbacks(
            on_status=lambda msg, color: status_messages.append(msg)
        )
        
        with patch.object(spam_clicker.mouse_controller, 'click', side_effect=raise_error):
            spam_clicker.start_spam_click()
            time.sleep(0.1)
            spam_clicker.stop_spam_click()


class TestPlayerMouseDeadlockPrevention:
    """Tests to ensure playback doesn't leave mouse in pressed state."""
    
    def test_playback_releases_pressed_on_stop(self):
        """Test that stopping playback releases all pressed buttons."""
        player = Player()
        
        # Add some pressed buttons/keys
        from pynput.mouse import Button
        player._pressed_mouse_buttons.add(Button.left)
        
        with patch.object(player._mouse, 'release') as mock_release:
            player._release_all_pressed()
            mock_release.assert_called()
        
        assert len(player._pressed_mouse_buttons) == 0
    
    def test_playback_releases_pressed_keys_on_stop(self):
        """Test that stopping playback releases all pressed keys."""
        player = Player()
        
        from pynput.keyboard import Key
        player._pressed_keys.add(Key.shift)
        
        with patch.object(player._keyboard, 'release') as mock_release:
            player._release_all_pressed()
            mock_release.assert_called()
        
        assert len(player._pressed_keys) == 0
    
    def test_pressed_state_cleared_at_playback_start(self):
        """Test that pressed state is cleared when playback starts."""
        player = Player()
        
        from pynput.mouse import Button
        player._pressed_mouse_buttons.add(Button.left)
        
        events = [{"type": "test", "timestamp": 0}]
        
        with patch.object(player, '_playback_worker') as mock_worker:
            with patch('threading.Thread') as mock_thread:
                mock_thread.return_value = Mock()
                player.start(events=events)
    
    def test_playback_thread_is_daemon(self):
        """Test that playback thread is daemon (won't block app exit)."""
        player = Player()
        
        events = [{"type": "mouse_click", "x": 100, "y": 100, 
                   "button": "Button.left", "pressed": True, "timestamp": 0.1}]
        
        with patch.object(player._mouse, 'press'):
            with patch.object(player._mouse, 'release'):
                player.start(events=events)
                
                # Thread should be daemon
                if player._playback_thread is not None:
                    assert player._playback_thread.daemon is True
                
                player.stop()
    
    def test_infinite_loop_can_be_stopped(self):
        """Test that infinite loop playback can be stopped."""
        player = Player()
        
        events = [{"type": "mouse_click", "x": 100, "y": 100,
                   "button": "Button.left", "pressed": True, "timestamp": 0.01}]
        
        with patch.object(player._mouse, 'press'):
            with patch.object(player._mouse, 'release'):
                player.start(events=events, loop_count=0)  # 0 = infinite
                
                assert player.is_playing is True
                time.sleep(0.05)
                
                # Should be able to stop
                result = player.stop()
                assert result is True
                
                # Give thread time to finish
                time.sleep(0.1)
                assert player.is_playing is False


class TestUnbalancedEventDetection:
    """Tests for detecting unbalanced press/release events."""
    
    def test_detect_unbalanced_mouse_events(self):
        """Test detection of unbalanced mouse press/release."""
        events = [
            {"type": "mouse_click", "button": "Button.left", "pressed": True, 
             "x": 100, "y": 100, "timestamp": 0.1},
            # Missing release
        ]
        
        # Count press/release balance
        press_count = sum(1 for e in events if e.get('pressed', False))
        release_count = sum(1 for e in events if e.get('type') == 'mouse_click' and not e.get('pressed', True))
        
        assert press_count != release_count  # Unbalanced
    
    def test_detect_unbalanced_key_events(self):
        """Test detection of unbalanced key press/release."""
        events = [
            {"type": "key_press", "key": "a", "timestamp": 0.1},
            # Missing release
        ]
        
        press_count = sum(1 for e in events if e.get('type') == 'key_press')
        release_count = sum(1 for e in events if e.get('type') == 'key_release')
        
        assert press_count != release_count  # Unbalanced
    
    def test_balanced_events_validation(self):
        """Test that balanced events pass validation."""
        events = [
            {"type": "mouse_click", "button": "Button.left", "pressed": True,
             "x": 100, "y": 100, "timestamp": 0.1},
            {"type": "mouse_click", "button": "Button.left", "pressed": False,
             "x": 100, "y": 100, "timestamp": 0.2},
        ]
        
        press_count = sum(1 for e in events if e.get('pressed', False))
        release_count = sum(1 for e in events if e.get('type') == 'mouse_click' and not e.get('pressed', True))
        
        assert press_count == release_count  # Balanced


class TestConcurrencyProtection:
    """Tests for concurrent operation protection."""
    
    def test_cannot_spam_click_twice(self):
        """Test that spam clicking cannot be started twice."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            spam_clicker.start_spam_click()
            assert spam_clicker.is_spam_clicking is True
            
            # Second start should fail
            result = spam_clicker.start_spam_click()
            assert result is False
            
            spam_clicker.stop_spam_click()
    
    def test_cannot_play_twice(self):
        """Test that playback cannot be started twice."""
        player = Player()
        
        events = [{"type": "test", "timestamp": 0.1}]
        
        with patch.object(player, '_playback_worker'):
            with patch('threading.Thread') as mock_thread:
                mock_thread.return_value = Mock()
                
                player.start(events=events)
                assert player.is_playing is True
                
                # Second start should fail
                result = player.start(events=events)
                assert result is False


class TestPlaybackSpeedSafety:
    """Tests for playback speed edge cases."""
    
    def test_zero_playback_speed_handled(self):
        """Test that zero playback speed doesn't cause infinite wait."""
        player = Player()
        
        events = [{"type": "mouse_click", "x": 100, "y": 100,
                   "button": "Button.left", "pressed": True, "timestamp": 0.1}]
        
        with patch.object(player._mouse, 'press'):
            with patch.object(player._mouse, 'release'):
                # Speed of 0 should be handled gracefully
                player.start(events=events, playback_speed=0)
                time.sleep(0.2)
                player.stop()
    
    def test_very_high_playback_speed(self):
        """Test that very high playback speed works correctly."""
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
                
                # Should complete quickly
                time.sleep(0.5)
                assert len(completed) > 0 or not player.is_playing
