import time
import psutil
import threading
from contextlib import contextmanager
from typing import Any

# ===== TIMING AND PERFORMANCE UTILITIES =====

@contextmanager
def timer(operation_name: str):
    """Context manager for timing operations"""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"{operation_name} took {elapsed:.2f}s")

# ===== AUTO-SAVE MANAGEMENT =====

class AutoSaveManager:
    """Manages auto-save functionality"""
    
    def __init__(self, save_interval=300):
        self.save_interval = save_interval
        self.timer = None
    
    # ===== AUTO-SAVE CONTROL METHODS =====
    
    def start_auto_save(self, save_callback):
        """Start auto-save timer"""
        self.timer = threading.Timer(self.save_interval, save_callback)
        self.timer.daemon = True
        self.timer.start()
    
    def stop_auto_save(self):
        """Stop auto-save timer"""
        if self.timer:
            self.timer.cancel()

# ===== SYSTEM HEALTH UTILITIES =====

def health_check_system() -> dict:
    """Check system resource health"""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }