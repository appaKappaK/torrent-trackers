import json
import os
import threading
import time
from typing import Dict, Any

DEFAULT_CONFIG = {
    "validation": {
        "max_workers": 10,
        "timeout": 10,
        "socket_timeout": 5
    },
    "gui": {
        "window_width": 800,
        "window_height": 600,
        "auto_scroll": True,
        "dark_mode": False
    },
    "trackers": {
        "default_ports": {
            "http": 80,
            "https": 443, 
            "udp": 6969
        }
    }
}

class Config:
    """Manages application configuration with batched saves"""
    
    def __init__(self, config_path: str = "tracker_manager_config.json"):
        self.config_path = config_path
        self.data = self.load_config()
        self._pending_saves = 0
        self._save_timer = None
        self._save_lock = threading.Lock()
    
    def load_config(self) -> Dict[str, Any]:
        """Load config from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        # Save default config
        self._save_config_immediate(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default=None):
        """Get config value using dot notation"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
    
    def set(self, key: str, value: Any, immediate=False):
        """Set config value with optional batching"""
        keys = key.split('.')
        config_ref = self.data
        for k in keys[:-1]:
            config_ref = config_ref.setdefault(k, {})
        config_ref[keys[-1]] = value
        
        if immediate:
            self._save_config_immediate()
        else:
            self._schedule_save()
    
    def _schedule_save(self):
        """Schedule a batched save"""
        with self._save_lock:
            self._pending_saves += 1
            
            # Cancel existing timer
            if self._save_timer:
                self._save_timer.cancel()
            
            # Save immediately if too many pending, or schedule delayed save
            if self._pending_saves >= 10:
                self._save_config_immediate()
                self._pending_saves = 0
            else:
                self._save_timer = threading.Timer(1.0, self._flush_pending_saves)
                self._save_timer.daemon = True
                self._save_timer.start()
    
    def __del__(self):
        """Cleanup timer on destruction"""
        try:
            self._flush_pending_saves()
            if self._save_timer:
                self._save_timer.cancel()
        except:
            pass  # Ignore errors during cleanup

    def _flush_pending_saves(self):
        """Flush pending saves to disk"""
        with self._save_lock:
            if self._pending_saves > 0:
                self._save_config_immediate()
                self._pending_saves = 0
                self._save_timer = None
    
    def _save_config_immediate(self, config_data: Dict[str, Any] = None):
        """Save config to file immediately"""
        data = config_data or self.data
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def save_config(self, config_data: Dict[str, Any] = None):
        """Public method to force immediate save"""
        self._save_config_immediate(config_data)
    
    def validate_config(self):
        """Enhanced configuration validation"""
        required_keys = [
            'validation.max_workers', 
            'validation.timeout',
            'validation.socket_timeout'
        ]
        
        for key in required_keys:
            if not self.get(key):
                raise ValueError(f"Missing required config: {key}")
                
        max_workers = self.get('validation.max_workers')
        if not 1 <= max_workers <= 50:
            raise ValueError("max_workers must be between 1 and 50")
        
        timeout = self.get('validation.timeout')
        if timeout <= 0:
            raise ValueError("timeout must be positive")
    
    def get_presets(self):
        """Get available tracker presets"""
        return TRACKER_PRESETS


# Add these constants after Config class
SUPPORTED_FORMATS = {
    'txt': 'Text file (.txt)',
    'json': 'JSON file (.json)', 
    'csv': 'CSV file (.csv)',
    'yaml': 'YAML file (.yaml)'
}

TRACKER_PRESETS = {
    'default': [
        'udp://tracker.opentrackr.org:1337/announce',
        'http://tracker.openbittorrent.com:80/announce',
        'udp://9.rarbg.to:2710/announce'
    ],
    'minimal': [
        'udp://tracker.opentrackr.org:1337/announce'
    ]
}