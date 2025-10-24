"""
Configuration Manager for QuantForge Backtest Manager
Handles saving and loading of application settings.
"""
import json
import os
from pathlib import Path


class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or return defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self):
        """Return default configuration."""
        return {
            "last_folder": "",
            "window_geometry": {
                "x": 100,
                "y": 100,
                "width": 1400,
                "height": 900
            },
            "splitter_state": None,
            "recent_folders": [],
            "imported_files": []  # List of imported file paths with status
        }
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, indent=4, fp=f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save."""
        self.config[key] = value
        self.save_config()
    
    def add_recent_folder(self, folder_path):
        """Add folder to recent folders list."""
        recent = self.config.get("recent_folders", [])
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        self.config["recent_folders"] = recent[:10]  # Keep only last 10
        self.save_config()
    
    def add_imported_file(self, file_path, status="not_run"):
        """Add an imported file with its status."""
        imported = self.config.get("imported_files", [])
        
        # Remove if already exists (to update)
        imported = [f for f in imported if f.get("path") != file_path]
        
        # Add the file with status
        imported.append({
            "path": file_path,
            "status": status
        })
        
        self.config["imported_files"] = imported
        self.save_config()
    
    def update_file_status(self, file_path, status):
        """Update the status of an imported file."""
        imported = self.config.get("imported_files", [])
        
        for file_entry in imported:
            if file_entry.get("path") == file_path:
                file_entry["status"] = status
                self.config["imported_files"] = imported
                self.save_config()
                return
        
        # If not found in imported files, add it
        self.add_imported_file(file_path, status)
    
    def get_imported_files(self):
        """Get list of imported files with their status."""
        return self.config.get("imported_files", [])
    
    def remove_imported_file(self, file_path):
        """Remove an imported file from the list."""
        imported = self.config.get("imported_files", [])
        imported = [f for f in imported if f.get("path") != file_path]
        self.config["imported_files"] = imported
        self.save_config()

