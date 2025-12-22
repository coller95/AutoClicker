"""Spam clicking functionality."""

from pynput.mouse import Button, Controller as MouseController
import threading
import time


class SpamClicker:
    """Manages rapid-fire spam clicking."""
    
    def __init__(self):
        self.mouse_controller = MouseController()
        self.is_spam_clicking = False
        self.spam_click_thread = None
        
        # Callbacks
        self.on_status_callback = None
    
    def set_callbacks(self, on_status=None):
        """Set callback functions for status updates."""
        if on_status:
            self.on_status_callback = on_status
    
    def start_spam_click(self):
        """Start rapid-fire left clicking."""
        if self.is_spam_clicking:
            return False
        
        self.is_spam_clicking = True
        
        if self.on_status_callback:
            self.on_status_callback("Spam clicking active!", "red")
        
        self.spam_click_thread = threading.Thread(target=self._spam_click_worker)
        self.spam_click_thread.daemon = True
        self.spam_click_thread.start()
        
        return True
    
    def _spam_click_worker(self):
        """Worker thread for rapid-fire clicking."""
        try:
            while self.is_spam_clicking:
                self.mouse_controller.click(Button.left, 1)
                time.sleep(0.01)  # 10ms delay = 100 clicks per second
        except Exception as e:
            if self.on_status_callback:
                self.on_status_callback(f"Error: {str(e)}", "red")
    
    def stop_spam_click(self):
        """Stop spam clicking."""
        if self.is_spam_clicking:
            self.is_spam_clicking = False
            if self.on_status_callback:
                self.on_status_callback("Spam clicking stopped!", "green")
            return True
        return False
    
    def is_active(self):
        """Check if spam clicking is currently active."""
        return self.is_spam_clicking
