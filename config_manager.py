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
            "recent_folders": []
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

