"""Unit tests for SpamClicker class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import threading

from models.spam_clicker import SpamClicker


class TestSpamClickerInit:
    """Tests for SpamClicker initialization."""
    
    def test_initial_state(self):
        """Test that SpamClicker initializes with correct default state."""
        clicker = SpamClicker()
        
        assert clicker.is_spam_clicking is False
        assert clicker.spam_click_thread is None
        assert clicker.on_status_callback is None
    
    def test_mouse_controller_initialized(self):
        """Test that mouse controller is initialized."""
        clicker = SpamClicker()
        
        assert clicker.mouse_controller is not None


class TestSpamClickerCallbacks:
    """Tests for SpamClicker callback functionality."""
    
    def test_set_status_callback(self):
        """Test setting status callback."""
        clicker = SpamClicker()
        mock_callback = Mock()
        
        clicker.set_callbacks(on_status=mock_callback)
        
        assert clicker.on_status_callback == mock_callback
    
    def test_set_callbacks_with_none(self):
        """Test that None callbacks are not set."""
        clicker = SpamClicker()
        clicker.on_status_callback = Mock()
        original_callback = clicker.on_status_callback
        
        clicker.set_callbacks(on_status=None)
        
        # Should keep the original callback
        assert clicker.on_status_callback == original_callback


class TestSpamClickerStartStop:
    """Tests for SpamClicker start/stop functionality."""
    
    def test_start_spam_click_changes_state(self):
        """Test that starting spam click changes state."""
        clicker = SpamClicker()
        
        with patch.object(threading.Thread, 'start'):
            result = clicker.start_spam_click()
        
        assert result is True
        assert clicker.is_spam_clicking is True
    
    def test_cannot_start_when_already_clicking(self):
        """Test that starting fails when already spam clicking."""
        clicker = SpamClicker()
        clicker.is_spam_clicking = True
        
        result = clicker.start_spam_click()
        
        assert result is False
    
    def test_start_triggers_status_callback(self):
        """Test that starting triggers the status callback."""
        clicker = SpamClicker()
        mock_callback = Mock()
        clicker.set_callbacks(on_status=mock_callback)
        
        with patch.object(threading.Thread, 'start'):
            clicker.start_spam_click()
        
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args[0]
        assert "Spam clicking" in call_args[0]
    
    def test_stop_spam_click_changes_state(self):
        """Test that stopping spam click changes state."""
        clicker = SpamClicker()
        clicker.is_spam_clicking = True
        
        result = clicker.stop_spam_click()
        
        assert clicker.is_spam_clicking is False
    
    def test_stop_when_not_clicking(self):
        """Test stopping when not currently spam clicking."""
        clicker = SpamClicker()
        clicker.is_spam_clicking = False
        
        result = clicker.stop_spam_click()
        
        # Should handle gracefully
        assert clicker.is_spam_clicking is False


class TestSpamClickerThread:
    """Tests for SpamClicker threading behavior."""
    
    def test_thread_is_daemon(self):
        """Test that the spam click thread is a daemon thread."""
        clicker = SpamClicker()
        
        with patch.object(threading.Thread, 'start'):
            clicker.start_spam_click()
        
        assert clicker.spam_click_thread.daemon is True
    
    def test_thread_created_on_start(self):
        """Test that a thread is created when starting."""
        clicker = SpamClicker()
        
        with patch.object(threading.Thread, 'start'):
            clicker.start_spam_click()
        
        assert clicker.spam_click_thread is not None
        assert isinstance(clicker.spam_click_thread, threading.Thread)
