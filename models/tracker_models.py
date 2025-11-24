from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import time
import re
from urllib.parse import urlparse
import logging
from functools import lru_cache

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class Tracker:
    """Represents a single tracker with its properties"""
    url: str
    alive: bool = False
    response_time: float = None
    error: str = None
    tracker_type: str = 'unknown'
    
    # ===== PROPERTY METHODS =====
    
    @property
    def normalized_url(self):
        return Tracker.normalize_tracker_url(self.url)
    
    # ===== URL PROCESSING METHODS =====
    
    @staticmethod
    def normalize_tracker_url(url: str) -> str:
        """Normalize tracker URL for duplicate detection"""
        url = url.lower().strip()
        
        # Remove common non-essential parameters and clean up trailing ?/&
        url = re.sub(r'[?&](tr|ws|as)=[^&]+', '', url)
        url = re.sub(r'[?&]+$', '', url)
        
        # Standardize magnet links
        if url.startswith('magnet:'):
            if match := re.search(r'[?&]xt=urn:btih:([a-fA-F0-9]{40}|[a-zA-Z2-7]{32})', url, re.I):
                return f"magnet:btih:{match.group(1).lower()}"
        
        return url

    @staticmethod
    @lru_cache(maxsize=1000)
    def normalize_tracker_url_cached(url: str) -> str:
        """Cached version for performance with size limit"""
        return Tracker.normalize_tracker_url(url)

    @staticmethod
    def clear_normalization_cache():
        """Clear the URL normalization cache"""
        Tracker.normalize_tracker_url_cached.cache_clear()

    @staticmethod
    def sanitize_tracker_url(url: str) -> Optional[str]:
        """Sanitize and validate tracker URLs"""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https', 'udp']:
                return None
            if not parsed.hostname:
                return None
            return url
        except:
            return None


class TrackerCollection:
    """Manages a collection of trackers with state"""
    
    def __init__(self):
        self.trackers: List[Tracker] = []
        self.unique_urls: List[str] = []
        self.validation_results: List[Tracker] = []
    
    # ===== COLLECTION MANAGEMENT METHODS =====
    
    def clear(self):
        """Clear all data"""
        self.trackers.clear()
        self.unique_urls.clear()
        self.validation_results.clear()
    
    # ===== PROPERTY METHODS =====
    
    @property
    def working_trackers(self) -> List[Tracker]:
        return [t for t in self.validation_results if t.alive]
    
    @property
    def dead_trackers(self) -> List[Tracker]:
        return [t for t in self.validation_results if not t.alive]


@dataclass
class ValidationResult:
    """Enhanced result class with timestamps"""
    url: str
    alive: bool
    response_time: Optional[float] = None
    error: Optional[str] = None
    tracker_type: str = 'unknown'
    validated_at: float = None
    
    # ===== INITIALIZATION METHODS =====
    
    def __post_init__(self):
        if self.validated_at is None:
            self.validated_at = time.time()


@dataclass
class TrackerStats:
    """Statistics data container"""
    total: int = 0
    working: int = 0
    dead: int = 0
    avg_response_time: float = 0.0
    by_type: Dict[str, int] = None
    
    # ===== INITIALIZATION METHODS =====
    
    def __post_init__(self):
        if self.by_type is None:
            self.by_type = {}