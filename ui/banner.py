"""Banner and border overlay management for visual feedback."""

import tkinter as tk


class BannerManager:
    """Manages on-screen banner and border overlays for visual feedback."""
    
    def __init__(self, root):
        self.root = root
        self.banner_window = None
        self.border_frames = []
    
    def show_banner(self, text, bg_color):
        """Show compact always-on-top banner at top-left with screen border."""
        if self.banner_window:
            self.hide_banner()
        
        # Create compact banner at top-left
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
        
        # Position at top-left corner
        self.banner_window.geometry(f"+10+10")
        
        # Create thin border frames around screen edges
        screen_width = self.banner_window.winfo_screenwidth()
        screen_height = self.banner_window.winfo_screenheight()
        border_thickness = 4
        
        # Top border
        top_frame = tk.Toplevel(self.root)
        top_frame.overrideredirect(True)
        top_frame.attributes('-topmost', True)
        top_frame.configure(bg=bg_color)
        top_frame.geometry(f"{screen_width}x{border_thickness}+0+0")
        self.border_frames.append(top_frame)
        
        # Bottom border
        bottom_frame = tk.Toplevel(self.root)
        bottom_frame.overrideredirect(True)
        bottom_frame.attributes('-topmost', True)
        bottom_frame.configure(bg=bg_color)
        bottom_frame.geometry(f"{screen_width}x{border_thickness}+0+{screen_height-border_thickness}")
        self.border_frames.append(bottom_frame)
        
        # Left border
        left_frame = tk.Toplevel(self.root)
        left_frame.overrideredirect(True)
        left_frame.attributes('-topmost', True)
        left_frame.configure(bg=bg_color)
        left_frame.geometry(f"{border_thickness}x{screen_height}+0+0")
        self.border_frames.append(left_frame)
        
        # Right border
        right_frame = tk.Toplevel(self.root)
        right_frame.overrideredirect(True)
        right_frame.attributes('-topmost', True)
        right_frame.configure(bg=bg_color)
        right_frame.geometry(f"{border_thickness}x{screen_height}+{screen_width-border_thickness}+0")
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
