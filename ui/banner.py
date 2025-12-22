"""Banner and border overlay management for visual feedback."""

import tkinter as tk


class BannerManager:
    """Manages on-screen banner and border overlays for visual feedback."""
    
    def __init__(self, root):
        self.root = root
        self.banner_windows = []  # List of banner windows (one per monitor)
        self.border_frames = []
    
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
    
    def show_banner(self, text, bg_color):
        """Show compact always-on-top banner and borders on ALL monitors.
        
        The banner appears at the top-left of each monitor, and colored borders
        surround each monitor's edges.
        """
        if self.banner_windows or self.border_frames:
            self.hide_banner()
        
        # Get all monitors
        monitors = self._get_all_monitors()
        border_thickness = 4
        
        for mon_x, mon_y, mon_width, mon_height in monitors:
            # Create compact banner at top-left of this monitor
            banner_window = tk.Toplevel(self.root)
            banner_window.overrideredirect(True)  # Remove window decorations
            banner_window.attributes('-topmost', True)  # Always on top
            
            # Create compact banner label
            banner_label = tk.Label(banner_window, text=text,
                                   font=("Arial", 11, "bold"),
                                   bg=bg_color, fg="white",
                                   padx=15, pady=8)
            banner_label.pack()
            
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
    
    def hide_banner(self):
        """Hide and destroy all banner windows and border frames."""
        for banner in self.banner_windows:
            try:
                banner.destroy()
            except:
                pass
        self.banner_windows = []
        
        for frame in self.border_frames:
            try:
                frame.destroy()
            except:
                pass
        self.border_frames = []
    
    def cleanup(self):
        """Clean up all banner resources."""
        self.hide_banner()
