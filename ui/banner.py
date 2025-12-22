"""Banner and border overlay management for visual feedback."""

import tkinter as tk


class BannerManager:
    """Manages on-screen banner and border overlays for visual feedback."""
    
    def __init__(self, root):
        self.root = root
        self.banner_windows = []  # List of banner windows (one per monitor)
        self.border_frames = []
        self.status_labels = []  # Status labels for updating messages
        self.input_labels = []   # Labels for showing live input
        self.countdown_labels = []  # Labels for showing countdown timer
        self.current_bg_color = None
        self.default_status = ""
        self.auto_hide_id = None  # For auto-hiding status messages
    
    def _get_all_monitors(self):
        """Get geometry of all monitors.
        
        Returns:
            list: List of tuples (x, y, width, height) for each monitor
        """
        monitors = []
        
        # Try to use screeninfo library for accurate multi-monitor detection
        try:
            from screeninfo import get_monitors
            for monitor in get_monitors():
                monitors.append((monitor.x, monitor.y, monitor.width, monitor.height))
        except ImportError:
            pass
        except Exception:
            pass
        
        # Fallback: use tkinter's screen dimensions (primary monitor only)
        if not monitors:
            monitors.append((0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        
        return monitors
    
    def show_banner(self, text, bg_color, status_text=None):
        """Show compact always-on-top banner and borders on ALL monitors.
        
        The banner appears at the top-left of each monitor, and colored borders
        surround each monitor's edges.
        
        Args:
            text: Main banner text (e.g., "● RECORDING")
            bg_color: Background color for banner and borders
            status_text: Optional status line (e.g., "Press F6 to stop")
        """
        if self.banner_windows or self.border_frames:
            self.hide_banner()
        
        self.current_bg_color = bg_color
        self.status_labels = []
        self.input_labels = []  # For showing live input
        self.countdown_labels = []  # For showing countdown timer
        self.default_status = status_text or ""
        
        # Get all monitors
        monitors = self._get_all_monitors()
        border_thickness = 4
        
        for mon_x, mon_y, mon_width, mon_height in monitors:
            # Create compact banner at top-left of this monitor
            banner_window = tk.Toplevel(self.root)
            banner_window.overrideredirect(True)  # Remove window decorations
            banner_window.attributes('-topmost', True)  # Always on top
            banner_window.configure(bg=bg_color)
            
            # Create frame to hold labels
            banner_frame = tk.Frame(banner_window, bg=bg_color)
            banner_frame.pack(padx=12, pady=8)
            
            # Main banner label
            banner_label = tk.Label(banner_frame, text=text,
                                   font=("Arial", 12, "bold"),
                                   bg=bg_color, fg="white")
            banner_label.pack(anchor="w")
            
            # Live input line (shows latest key/mouse)
            input_label = tk.Label(banner_frame, text="",
                                  font=("Arial", 10),
                                  bg=bg_color, fg="#FFEB3B",  # Yellow for visibility
                                  width=25, anchor="w")
            input_label.pack(anchor="w")
            self.input_labels.append(input_label)
            
            # Countdown timer label (shows delay countdown between loops)
            countdown_label = tk.Label(banner_frame, text="",
                                       font=("Arial", 11, "bold"),
                                       bg=bg_color, fg="#4FC3F7",  # Light blue for visibility
                                       anchor="w")
            countdown_label.pack(anchor="w")
            self.countdown_labels.append(countdown_label)
            
            # Status line (smaller, below main text)
            status_label = tk.Label(banner_frame, text=status_text or "",
                                   font=("Arial", 9),
                                   bg=bg_color, fg="white")
            status_label.pack(anchor="w")
            self.status_labels.append(status_label)
            
            # Update geometry after packing to get actual size
            banner_window.update_idletasks()
            
            # Position at top-left corner of this monitor
            banner_window.geometry(f"+{mon_x + 10}+{mon_y + 10}")
            self.banner_windows.append(banner_window)
            
            # Create thin border frames around this monitor's edges
            
            # Top border
            top_frame = tk.Toplevel(self.root)
            top_frame.overrideredirect(True)
            top_frame.attributes('-topmost', True)
            top_frame.configure(bg=bg_color)
            top_frame.geometry(f"{mon_width}x{border_thickness}+{mon_x}+{mon_y}")
            self.border_frames.append(top_frame)
            
            # Bottom border
            bottom_frame = tk.Toplevel(self.root)
            bottom_frame.overrideredirect(True)
            bottom_frame.attributes('-topmost', True)
            bottom_frame.configure(bg=bg_color)
            bottom_frame.geometry(f"{mon_width}x{border_thickness}+{mon_x}+{mon_y + mon_height - border_thickness}")
            self.border_frames.append(bottom_frame)
            
            # Left border
            left_frame = tk.Toplevel(self.root)
            left_frame.overrideredirect(True)
            left_frame.attributes('-topmost', True)
            left_frame.configure(bg=bg_color)
            left_frame.geometry(f"{border_thickness}x{mon_height}+{mon_x}+{mon_y}")
            self.border_frames.append(left_frame)
            
            # Right border
            right_frame = tk.Toplevel(self.root)
            right_frame.overrideredirect(True)
            right_frame.attributes('-topmost', True)
            right_frame.configure(bg=bg_color)
            right_frame.geometry(f"{border_thickness}x{mon_height}+{mon_x + mon_width - border_thickness}+{mon_y}")
            self.border_frames.append(right_frame)
    
    def update_live_input(self, input_type, input_text):
        """Update the live input display on all banners.
        
        Args:
            input_type: Type of input ("key" or "mouse")
            input_text: The text to display (e.g., "⌨ A" or "🖱 LEFT (100, 200)")
        """
        if not self.banner_windows:
            return
        
        # Update all input labels
        for label in self.input_labels:
            try:
                label.config(text=input_text)
            except:
                pass
        
        # Update window geometry to fit new text
        for window in self.banner_windows:
            try:
                window.update_idletasks()
            except:
                pass
    
    def update_countdown(self, remaining_seconds):
        """Update the countdown timer display on all banners.
        
        Args:
            remaining_seconds: Seconds remaining in the delay (0 to hide)
        """
        if not self.banner_windows:
            return
        
        # Format countdown text
        if remaining_seconds > 0:
            countdown_text = f"⏱ Next loop in: {remaining_seconds:.1f}s"
        else:
            countdown_text = ""
        
        # Update all countdown labels
        for label in self.countdown_labels:
            try:
                label.config(text=countdown_text)
            except:
                pass
        
        # Update window geometry to fit new text
        for window in self.banner_windows:
            try:
                window.update_idletasks()
            except:
                pass
    
    def update_status(self, message, default_status=None, duration=2000):
        """Update the status text on all banners.
        
        Args:
            message: The status message to display
            default_status: The default status to revert to after duration (optional)
            duration: Time in ms before reverting to default_status (default 2000ms)
        """
        if not self.banner_windows:
            return
        
        # Cancel any pending auto-hide
        if self.auto_hide_id:
            self.root.after_cancel(self.auto_hide_id)
            self.auto_hide_id = None
        
        # Update all status labels
        for label in self.status_labels:
            try:
                label.config(text=message)
            except:
                pass
        
        # Update window geometry to fit new text
        for window in self.banner_windows:
            try:
                window.update_idletasks()
            except:
                pass
        
        # If default_status provided, revert after duration
        if default_status is not None:
            self.auto_hide_id = self.root.after(duration, lambda: self._revert_status(default_status))
    
    def _revert_status(self, default_status):
        """Revert status labels to default text."""
        self.auto_hide_id = None
        for label in self.status_labels:
            try:
                label.config(text=default_status)
            except:
                pass
        # Update window geometry
        for window in self.banner_windows:
            try:
                window.update_idletasks()
            except:
                pass
    
    def show_status_message(self, message, color="#333333", duration=2000):
        """Show a temporary status message banner (when no action banner is active).
        
        Args:
            message: The message to display
            color: Background color (default dark gray)
            duration: Time in ms before auto-hiding (default 2000ms)
        """
        # Only show if no active banner
        if self.banner_windows:
            return
        
        # Cancel any pending auto-hide
        if self.auto_hide_id:
            self.root.after_cancel(self.auto_hide_id)
            self.auto_hide_id = None
        
        # Get all monitors
        monitors = self._get_all_monitors()
        
        for mon_x, mon_y, mon_width, mon_height in monitors:
            # Create compact message banner
            banner_window = tk.Toplevel(self.root)
            banner_window.overrideredirect(True)
            banner_window.attributes('-topmost', True)
            banner_window.configure(bg=color)
            
            # Message label
            msg_label = tk.Label(banner_window, text=message,
                                font=("Arial", 10, "bold"),
                                bg=color, fg="white",
                                padx=15, pady=8)
            msg_label.pack()
            
            banner_window.update_idletasks()
            banner_window.geometry(f"+{mon_x + 10}+{mon_y + 10}")
            self.banner_windows.append(banner_window)
        
        # Auto-hide after duration
        self.auto_hide_id = self.root.after(duration, self.hide_banner)
    
    def hide_banner(self):
        """Hide and destroy all banner windows and border frames."""
        # Cancel any pending auto-hide
        if self.auto_hide_id:
            self.root.after_cancel(self.auto_hide_id)
            self.auto_hide_id = None
        
        for banner in self.banner_windows:
            try:
                banner.destroy()
            except:
                pass
        self.banner_windows = []
        self.status_labels = []
        self.input_labels = []
        self.countdown_labels = []
        self.current_bg_color = None
        self.default_status = ""
        
        for frame in self.border_frames:
            try:
                frame.destroy()
            except:
                pass
        self.border_frames = []
    
    def cleanup(self):
        """Clean up all banner resources."""
        self.hide_banner()
