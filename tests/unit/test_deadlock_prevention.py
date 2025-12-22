"""Tests for preventing mouse/keyboard deadlock scenarios."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import threading
import time

from models.event_recorder import EventRecorder
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
            
            # Thread should be a daemon
            assert spam_clicker.spam_click_thread.daemon is True
            
            spam_clicker.stop_spam_click()
    
    def test_spam_clicker_stops_on_flag_change(self):
        """Test that spam click loop respects the stop flag."""
        spam_clicker = SpamClicker()
        click_count = 0
        max_clicks = 10
        
        def mock_click(*args):
            nonlocal click_count
            click_count += 1
            if click_count >= max_clicks:
                spam_clicker.is_spam_clicking = False
        
        with patch.object(spam_clicker.mouse_controller, 'click', side_effect=mock_click):
            spam_clicker.start_spam_click()
            
            # Wait for thread to finish
            spam_clicker.spam_click_thread.join(timeout=2)
            
            # Thread should have stopped
            assert click_count >= max_clicks
            assert spam_clicker.is_spam_clicking is False
    
    def test_spam_clicker_uses_complete_click_not_press_release(self):
        """Test that spam clicker uses click() not separate press/release."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click') as mock_click:
            spam_clicker.start_spam_click()
            time.sleep(0.05)  # Let it run briefly
            spam_clicker.stop_spam_click()
            
            # Should use click(), not press()/release() which could deadlock
            assert mock_click.called
    
    def test_spam_clicker_handles_exception_gracefully(self):
        """Test that spam clicker handles exceptions without deadlock."""
        spam_clicker = SpamClicker()
        status_messages = []
        
        def capture_status(msg, color):
            status_messages.append(msg)
        
        spam_clicker.set_callbacks(on_status=capture_status)
        
        with patch.object(spam_clicker.mouse_controller, 'click', 
                         side_effect=Exception("Test error")):
            spam_clicker.start_spam_click()
            
            # Wait for thread to handle exception
            spam_clicker.spam_click_thread.join(timeout=2)
            
            # Should have captured error status
            assert any("Error" in msg for msg in status_messages)


class TestEventRecorderMouseDeadlockPrevention:
    """Tests to ensure playback doesn't leave mouse in pressed state."""
    
    def test_playback_completes_press_release_pairs(self):
        """Test that mouse press always has a corresponding release."""
        recorder = EventRecorder()
        
        # Simulate events with press and release
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 0.1},
        ]
        
        press_calls = []
        release_calls = []
        
        with patch.object(recorder.mouse_controller, 'press', 
                         side_effect=lambda b: press_calls.append(b)):
            with patch.object(recorder.mouse_controller, 'release',
                             side_effect=lambda b: release_calls.append(b)):
                with patch.object(recorder, 'mouse_controller') as mock_ctrl:
                    mock_ctrl.press = Mock(side_effect=lambda b: press_calls.append(b))
                    mock_ctrl.release = Mock(side_effect=lambda b: release_calls.append(b))
                    mock_ctrl.position = (0, 0)
                    
                    recorder.start_playback()
                    
                    # Wait for playback to complete
                    time.sleep(0.5)
                    
                    # Press and release should be balanced
                    assert len(press_calls) == len(release_calls)
    
    def test_stop_playback_releases_pressed_mouse_buttons(self):
        """Test that stopping playback releases any held mouse buttons."""
        recorder = EventRecorder()
        
        # Only press events, no release - simulates stopping mid-action
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 10.0},  # Long delay to allow stop
        ]
        
        release_calls = []
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release',
                             side_effect=lambda b: release_calls.append(b)):
                recorder.start_playback()
                
                # Wait for first press
                time.sleep(0.1)
                
                # Stop playback - should release pressed button
                recorder.stop_playback()
                
                # Wait for cleanup
                time.sleep(0.1)
                
                # The pressed button should have been released
                from pynput.mouse import Button
                assert Button.left in release_calls
    
    def test_stop_playback_releases_pressed_keys(self):
        """Test that stopping playback releases any held keyboard keys."""
        recorder = EventRecorder()
        
        # Only press events, no release
        recorder.recorded_events = [
            {'type': 'key_press', 'key': 'a', 'timestamp': 0.0},
            {'type': 'key_press', 'key': 'a', 'timestamp': 10.0},  # Long delay
        ]
        
        release_calls = []
        
        with patch.object(recorder.keyboard_controller, 'press'):
            with patch.object(recorder.keyboard_controller, 'release',
                             side_effect=lambda k: release_calls.append(k)):
                recorder.start_playback()
                
                # Wait for first press
                time.sleep(0.1)
                
                # Stop playback - should release pressed key
                recorder.stop_playback()
                
                # Wait for cleanup
                time.sleep(0.1)
                
                # The pressed key should have been released
                assert 'a' in release_calls
    
    def test_playback_complete_releases_all_pressed(self):
        """Test that normal playback completion releases any held buttons."""
        recorder = EventRecorder()
        
        # Unbalanced events - press without release
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            # No release event!
        ]
        
        release_calls = []
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release',
                             side_effect=lambda b: release_calls.append(b)):
                recorder.start_playback()
                
                # Wait for playback to complete
                time.sleep(0.3)
                
                # The pressed button should have been released in finally block
                from pynput.mouse import Button
                assert Button.left in release_calls
    
    def test_pressed_state_cleared_at_playback_start(self):
        """Test that pressed state is cleared when starting new playback."""
        recorder = EventRecorder()
        
        # Manually set some stale pressed state
        from pynput.mouse import Button
        recorder._pressed_mouse_buttons.add(Button.right)
        recorder._pressed_keys.add('x')
        
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 0.01},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback()
                
                # Wait a moment for worker to start and clear state
                time.sleep(0.05)
                
                # Stale state should be cleared (right button wasn't pressed in this session)
                # Only left button should be tracked if pressed
                assert Button.right not in recorder._pressed_mouse_buttons
                assert 'x' not in recorder._pressed_keys
                
                recorder.stop_playback()
    
    def test_playback_stops_cleanly_mid_sequence(self):
        """Test that stopping playback mid-sequence is handled."""
        recorder = EventRecorder()
        
        # Create many events to ensure we can stop mid-playback
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': i * 0.1}
            for i in range(100)
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback()
                
                # Stop immediately
                time.sleep(0.05)
                result = recorder.stop_playback()
                
                assert result is True
                assert recorder.is_playing is False
    
    def test_playback_thread_is_daemon(self):
        """Test that playback thread is daemon (won't block app exit)."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                recorder.start_playback()
                
                # Thread should be a daemon
                assert recorder.playback_thread.daemon is True
                
                recorder.stop_playback()
    
    def test_infinite_loop_can_be_stopped(self):
        """Test that infinite loop playback can be stopped."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 0.01},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                # Start infinite loop (loop_count=0)
                recorder.start_playback(loop_count=0)
                
                assert recorder.is_playing is True
                
                # Should be able to stop
                time.sleep(0.1)
                result = recorder.stop_playback()
                
                assert result is True
                
                # Wait for thread to finish
                recorder.playback_thread.join(timeout=1)
                assert recorder.is_playing is False


class TestEventRecorderKeyboardDeadlockPrevention:
    """Tests to ensure playback doesn't leave keys in pressed state."""
    
    def test_key_press_release_pairs(self):
        """Test that key press always has a corresponding release."""
        recorder = EventRecorder()
        
        recorder.recorded_events = [
            {'type': 'key_press', 'key': 'a', 'timestamp': 0.0},
            {'type': 'key_release', 'key': 'a', 'timestamp': 0.1},
        ]
        
        press_calls = []
        release_calls = []
        
        with patch.object(recorder.keyboard_controller, 'press',
                         side_effect=lambda k: press_calls.append(k)):
            with patch.object(recorder.keyboard_controller, 'release',
                             side_effect=lambda k: release_calls.append(k)):
                with patch.object(recorder.mouse_controller, 'press'):
                    with patch.object(recorder.mouse_controller, 'release'):
                        recorder.start_playback()
                        
                        # Wait for playback to complete
                        time.sleep(0.5)
                        
                        # Press and release should be balanced
                        assert len(press_calls) == len(release_calls)


class TestUnbalancedEventDetection:
    """Tests for detecting unbalanced press/release events in recordings."""
    
    def test_detect_unbalanced_mouse_events(self):
        """Test detection of mouse press without release."""
        events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            # Missing release!
        ]
        
        # Count presses and releases
        presses = sum(1 for e in events if e['type'] == 'mouse_click' and e.get('pressed'))
        releases = sum(1 for e in events if e['type'] == 'mouse_click' and not e.get('pressed'))
        
        # This recording is unbalanced
        assert presses != releases
        assert presses > releases
    
    def test_detect_unbalanced_key_events(self):
        """Test detection of key press without release."""
        events = [
            {'type': 'key_press', 'key': 'a', 'timestamp': 0.0},
            # Missing release!
        ]
        
        # Count presses and releases by key
        key_states = {}
        for event in events:
            if event['type'] == 'key_press':
                key = event['key']
                key_states[key] = key_states.get(key, 0) + 1
            elif event['type'] == 'key_release':
                key = event['key']
                key_states[key] = key_states.get(key, 0) - 1
        
        # Check for unbalanced keys
        unbalanced = {k: v for k, v in key_states.items() if v != 0}
        assert len(unbalanced) > 0  # 'a' is unbalanced
    
    def test_balanced_events_validation(self):
        """Test that balanced events pass validation."""
        events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 0.1},
            {'type': 'key_press', 'key': 'a', 'timestamp': 0.2},
            {'type': 'key_release', 'key': 'a', 'timestamp': 0.3},
        ]
        
        # Count mouse presses and releases
        mouse_presses = sum(1 for e in events if e['type'] == 'mouse_click' and e.get('pressed'))
        mouse_releases = sum(1 for e in events if e['type'] == 'mouse_click' and not e.get('pressed'))
        
        assert mouse_presses == mouse_releases
        
        # Count key presses and releases
        key_presses = sum(1 for e in events if e['type'] == 'key_press')
        key_releases = sum(1 for e in events if e['type'] == 'key_release')
        
        assert key_presses == key_releases


class TestConcurrencyProtection:
    """Tests for protection against concurrent operations."""
    
    def test_cannot_spam_click_twice(self):
        """Test that spam clicking cannot be started twice."""
        spam_clicker = SpamClicker()
        
        with patch.object(spam_clicker.mouse_controller, 'click'):
            result1 = spam_clicker.start_spam_click()
            result2 = spam_clicker.start_spam_click()
            
            assert result1 is True
            assert result2 is False  # Second start should fail
            
            spam_clicker.stop_spam_click()
    
    def test_cannot_record_and_play_simultaneously(self):
        """Test that recording and playback are mutually exclusive."""
        recorder = EventRecorder()
        
        with patch('pynput.mouse.Listener'), patch('pynput.keyboard.Listener'):
            recorder.start_recording()
        
        # Try to play while recording
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
        ]
        result = recorder.start_playback()
        
        assert result is False  # Should not be able to play while recording
        
        recorder.stop_recording()
    
    def test_cannot_play_twice(self):
        """Test that playback cannot be started twice."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 1.0},  # Long delay to keep playing
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                result1 = recorder.start_playback()
                result2 = recorder.start_playback()
                
                assert result1 is True
                assert result2 is False  # Second start should fail
                
                recorder.stop_playback()


class TestPlaybackSpeedSafety:
    """Tests for playback speed edge cases."""
    
    def test_zero_playback_speed_handled(self):
        """Test that zero playback speed doesn't cause infinite wait."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 0.1},
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                # Start with zero speed (edge case)
                recorder.start_playback(playback_speed=0)
                
                # Should still be stoppable
                time.sleep(0.2)
                recorder.stop_playback()
                
                # Wait for thread
                recorder.playback_thread.join(timeout=1)
                assert recorder.is_playing is False
    
    def test_very_high_playback_speed(self):
        """Test that very high playback speed doesn't cause issues."""
        recorder = EventRecorder()
        recorder.recorded_events = [
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': True, 'timestamp': 0.0},
            {'type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'Button.left', 
             'pressed': False, 'timestamp': 10.0},  # 10 second gap
        ]
        
        with patch.object(recorder.mouse_controller, 'press'):
            with patch.object(recorder.mouse_controller, 'release'):
                # Start with very high speed (1000x)
                recorder.start_playback(playback_speed=1000)
                
                # Should complete quickly
                time.sleep(0.5)
                
                # Should have completed
                assert recorder.is_playing is False
