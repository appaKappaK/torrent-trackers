from abc import ABC, abstractmethod
from typing import List
from models import Tracker

class Plugin(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def before_validation(self, trackers: List[Tracker]) -> List[Tracker]:
        """Called before validation starts"""
        return trackers
    
    @abstractmethod  
    def after_validation(self, results: List[Tracker]) -> List[Tracker]:
        """Called after validation completes"""
        return results

class DuplicateRemoverPlugin(Plugin):
    """Plugin to remove duplicates before validation"""
    
    def before_validation(self, trackers: List[Tracker]) -> List[Tracker]:
        seen = set()
        unique = []
        for tracker in trackers:
            if tracker.normalized_url not in seen:
                seen.add(tracker.normalized_url)
                unique.append(tracker)
        return unique
    
    def after_validation(self, results: List[Tracker]) -> List[Tracker]:
        return results

class StatsPlugin(Plugin):
    """Plugin to collect statistics"""
    
    def before_validation(self, trackers: List[Tracker]) -> List[Tracker]:
        return trackers
    
    def after_validation(self, results: List[Tracker]) -> List[Tracker]:
        # Could log stats or update UI here
        working = sum(1 for r in results if r.alive)
        print(f"Validation complete: {working}/{len(results)} working")
        return results