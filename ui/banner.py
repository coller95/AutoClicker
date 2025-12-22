"""Banner and border overlay management for visual feedback."""

import tkinter as tk


class BannerManager:
    """Manages on-screen banner and border overlays for visual feedback."""
    
    def __init__(self, root):
        self.root = root
        self.banner_window = None
        self.border_frames = []
    
    def _get_current_monitor_geometry(self):
        """Get the geometry of the monitor where the main window is located.
        
        Returns:
            tuple: (x, y, width, height) of the current monitor
        """
        # Get main window position
        win_x = self.root.winfo_x()
        win_y = self.root.winfo_y()
        win_center_x = win_x + self.root.winfo_width() // 2
        win_center_y = win_y + self.root.winfo_height() // 2
        
        # Try to use screeninfo library for accurate multi-monitor detection
        try:
            from screeninfo import get_monitors
            monitors = get_monitors()
            
            # Find which monitor contains the center of the main window
            for monitor in monitors:
                if (monitor.x <= win_center_x < monitor.x + monitor.width and
                    monitor.y <= win_center_y < monitor.y + monitor.height):
                    return (monitor.x, monitor.y, monitor.width, monitor.height)
            
            # If window center not in any monitor, find the closest one
            if monitors:
                # Default to the monitor that contains the window's top-left corner
                for monitor in monitors:
                    if (monitor.x <= win_x < monitor.x + monitor.width and
                        monitor.y <= win_y < monitor.y + monitor.height):
                        return (monitor.x, monitor.y, monitor.width, monitor.height)
                
                # Fallback to first monitor
                m = monitors[0]
                return (m.x, m.y, m.width, m.height)
        except ImportError:
            pass
        except Exception:
            pass
        
        # Fallback: use tkinter's screen dimensions (primary monitor only)
        # This is the legacy behavior for systems without screeninfo
        return (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
    
    def show_banner(self, text, bg_color):
        """Show compact always-on-top banner at top-left with screen border.
        
        The banner and borders are shown on the monitor where the main window is located.
        """
        if self.banner_window:
            self.hide_banner()
        
        # Get the geometry of the current monitor
        mon_x, mon_y, mon_width, mon_height = self._get_current_monitor_geometry()
        
        # Create compact banner at top-left of current monitor
        self.banner_window = tk.Toplevel(self.root)
        self.banner_window.overrideredirect(True)  # Remove window decorations
        self.banner_window.attributes('-topmost', True)  # Always on top
        
        # Create compact banner label
        banner_label = tk.Label(self.banner_window, text=text,
                               font=("Arial", 11, "bold"),
                               bg=bg_color, fg="white",
                               padx=15, pady=8)
        banner_label.pack()
        
        # Update geometry after packing to get actual size
        self.banner_window.update_idletasks()
        
        # Position at top-left corner of current monitor
        self.banner_window.geometry(f"+{mon_x + 10}+{mon_y + 10}")
        
        # Create thin border frames around current monitor edges
        border_thickness = 4
        
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
    
    def hide_banner(self):
        """Hide and destroy the banner window and border frames."""
        if self.banner_window:
            self.banner_window.destroy()
            self.banner_window = None
        
        for frame in self.border_frames:
            frame.destroy()
        self.border_frames = []
    
    def cleanup(self):
        """Clean up all banner resources."""
        self.hide_banner()
