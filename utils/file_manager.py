"""File management for saving and loading recordings."""

from tkinter import filedialog, messagebox
import json
import os


class FileManager:
    """Manages saving and loading of recording files."""
    
    @staticmethod
    def save_recording(events, config_data=None):
        """
        Save recorded events and configuration to a JSON file.
        
        Args:
            events: List of recorded events
            config_data: Optional dictionary with configuration settings
            
        Returns:
            tuple: (success: bool, filepath: str or None, message: str)
        """
        if not events:
            messagebox.showwarning("No Recording", "There are no recorded events to save!")
            return (False, None, "No events to save")
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".aclk",
            filetypes=[("AutoClicker Recording", "*.aclk"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Recording As"
        )
        
        if not file_path:
            return (False, None, "Save cancelled")
        
        try:
            # Prepare data structure
            if config_data:
                data = {
                    "events": events,
                    "config": config_data
                }
            else:
                data = events
            
            # Save to JSON file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            messagebox.showinfo("Success", 
                              f"Recording saved successfully!\n{len(events)} events saved to:\n{os.path.basename(file_path)}")
            return (True, file_path, f"Recording saved: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recording:\n{str(e)}")
            return (False, None, f"Error saving recording: {str(e)}")
    
    @staticmethod
    def load_recording():
        """
        Load recorded events and configuration from a JSON file.
        
        Returns:
            tuple: (success: bool, events: list or None, config: dict or None, message: str)
        """
        # Ask user for file to load
        file_path = filedialog.askopenfilename(
            filetypes=[("AutoClicker Recording", "*.aclk"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Recording"
        )
        
        if not file_path:
            return (False, None, None, "Load cancelled")
        
        try:
            # Load data from JSON file
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
            
            # Check if it's the new format (with config) or old format (just events)
            if isinstance(loaded_data, dict) and 'events' in loaded_data:
                # New format: has events and config
                loaded_events = loaded_data['events']
                config = loaded_data.get('config', {})
            else:
                # Old format: just events
                loaded_events = loaded_data
                config = {}
            
            # Validate the loaded events
            if not isinstance(loaded_events, list):
                raise ValueError("Invalid file format: expected a list of events")
            
            # Basic validation of event structure
            for event in loaded_events:
                if not isinstance(event, dict):
                    raise ValueError("Invalid event format: expected dictionary")
                if 'type' not in event or 'timestamp' not in event:
                    raise ValueError("Invalid event format: missing required fields")
            
            messagebox.showinfo("Success", 
                              f"Recording loaded successfully!\n{len(loaded_events)} events loaded from:\n{os.path.basename(file_path)}")
            return (True, loaded_events, config, 
                   f"Recording loaded: {os.path.basename(file_path)} ({len(loaded_events)} events)")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to parse JSON file:\n{str(e)}")
            return (False, None, None, "Error loading recording: Invalid JSON")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recording:\n{str(e)}")
            return (False, None, None, f"Error loading recording: {str(e)}")
    
    @staticmethod
    def format_events_for_display(events):
        """
        Format events as text for display in a log.
        
        Args:
            events: List of recorded events
            
        Returns:
            str: Formatted text for display
        """
        lines = []
        for event in events:
            timestamp = event['timestamp']
            if event['type'] == 'mouse_click':
                action = "Press" if event['pressed'] else "Release"
                lines.append(f"[{timestamp:.2f}s] Mouse {action}: {event['button']} at ({event['x']}, {event['y']})")
            elif event['type'] == 'key_press':
                lines.append(f"[{timestamp:.2f}s] Key Press: {event['key']}")
            elif event['type'] == 'key_release':
                lines.append(f"[{timestamp:.2f}s] Key Release: {event['key']}")
            else:
                lines.append(f"[{timestamp:.2f}s] Unknown event type: {event['type']}")
        
        return '\n'.join(lines)
